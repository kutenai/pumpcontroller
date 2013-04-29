__author__ = 'kutenai'

from threading import RLock
import re
import os.path
import os,atexit
import json

from time import time,localtime,gmtime,strftime,sleep
import signal
import sys
import argparse

from DitchRedisHandler import DitchRedisHandler

from IrrigationAPIAT import IrrigationAPI
from DitchLogger import DitchLogger

import resource

class DitchManager(DitchRedisHandler):
    """

    Manage the ditch interface.
    Periodically read the levels and log them to the database, and to the COSM api

    Look for control inforation in redis. Redis can be used to set the pump and ditch
     control values, so, you can set the pump to 'on', and the north or south valves to
     'on', thus instructing the manager to send the appropriate commands.



    """

    def __init__(self, host='localhost', port=6388, db=0):
        super(DitchManager,self).__init__(host,port,db)

        self._debug = False
        self.resultBuffer = []
        self.statusBuffer = []
        self.enRun = True
        self.enDequeue = True
        self.isDaemon = False

        # For logging to COSM
        self.apikey = "d8ytNTiS45sNRIVqsluvbDTlW2eSAKxJVUNVamJLUmtJZz0g"


        self.api = IrrigationAPI()
        self.api.setPrintObj(self)

        self.loggr = DitchLogger(self.api)
        self.loggr.setPrintObj(self)

        self.txt = ""
        self.txtChanged = False

        self.msglock = RLock()
        self.printlock = RLock()

        self.hbCounter = 0
        # Heartbeat is ever n/10 seconds. This is 300 seconds, or 5 minutes
        self.hbSeconds = 300
        self.startTime = localtime()

        self.logfile = None
        self.logfp = None

        self.currCommandValues = {
            'pump' : False,
            'north' : False,
            'south' : False
        }

        self.cosmLogInterval = 60
        self.dbLogInterval = 60
        self.lastCosmLogTime = time() - 100
        self.lastDBLogTime = time() - 100

        def signal_handler(signal,frame):
            print("Keyboard interrupt!.")
            self.enRun = False
            sleep(1)
            sys.exit(0)

        def onterm(signal,frame):
            self.logprint("Termination received.")
            self.enRun = False
            self.logprint("Shutdown complete..")

        def onGracefulStop(signal,frame):
            self.enDequeue = False
            self.logprint("Graceful stop received. Initiating shutdown..")
            # Wait for the run flag to be cleared, meaning all sims are done.

        signal.signal(signal.SIGINT,signal_handler)
        signal.signal(signal.SIGTERM,onterm)
        signal.signal(signal.SIGUSR1,onGracefulStop)

    def start(self):
        """
        Tasks to perform after we have been Daemonized.. if that is how we are started.
        """

        self.startTime = gmtime()
        startTime = strftime("%a, %d %b %Y %H:%M:%S -0007", self.startTime)

        self.api.Initialize()

        self.logprint("Ditch Manager starting at " + startTime)

    def run(self):

        if self.isDaemon:
            self.start()
            atexit.register(self.shutdown)

        self.redisConnect() # attempt to connect
        self.initRedisValues()

        self.logprint("Starting Ditch Manager %s." % (self.myid))

        while self.enRun:
            if not self.isConnected:
                sleep(5) # Retry at 5 second intervals
                self.redisConnect()
                continue # Jump back to the top while loop

            # Do some things
            self.logCurrentLevels()

            self.checkCommandValues()

            # Do maintenance in between actions, or when
            # there are no sims to process
            self.processLogMessages()
            self.processMessages()

            sleep(0.5)


        self.redisDisconnect()

    def initRedisValues(self):
        """
        Read the redis values. Initialize them if they don't exist,
        and store our copies if they do.
        """
        pRequest = self.redis.get('pumprequest');
        nRequest= self.redis.get('northrequest');
        sRequest= self.redis.get('southrequest');

        if pRequest == None:
            self.redis.set('pumprequest',0)
            pRequest = '0'
        if nRequest == None:
            self.redis.set('northrequest',0)
            nRequest = '0'
        if sRequest == None:
            self.redis.set('southrequest',0)
            sRequest = '0'

        self.currCommandValues['pump'] = pRequest != '0'
        self.currCommandValues['north'] = nRequest  != '0'
        self.currCommandValues['south'] = sRequest  != '0'


    def checkCommandValues(self):
        """
        Determine if any of the redis command values have changed.

        If so, then send the appropriate commands

        """

        pRequest = self.redis.get('pumprequest');
        nRequest= self.redis.get('northrequest');
        sRequest= self.redis.get('southrequest');

        cmds = {
            'pump' : pRequest != '0',
            'north' : nRequest != '0',
            'south' : sRequest != '0'
        }

        for key in cmds.iterkeys():
            if cmds[key] != self.currCommandValues[key]:
                self.api.sendBool(key,cmds[key])
                self.lprint("%s set to %s" % (key,cmds[key]))
                self.currCommandValues[key] = cmds[key]

                if key == 'pump' and cmds[key]:
                    self.dbLogInterval = 5

    def logCurrentLevels(self):
        """
        Query the levels from the Ditch Unit, and log them.
        """

        dbDiff = time() - self.lastDBLogTime
        cosmDiff = time() - self.lastCosmLogTime

        if dbDiff > self.dbLogInterval or cosmDiff > self.cosmLogInterval:

            status = self.api.getSystemStatus()
            if status:

                if cosmDiff > self.cosmLogInterval:
                    self.lastCosmLogTime = time()
                    self.loggr.logResultsCosm(status['Ditch'],status['Sump'])
                if dbDiff > self.dbLogInterval:
                    self.lastDBLogTime = time()
                    self.loggr.logResultsDB(status)

                self.upateRedis(status)

    def upateRedis(self,status):

        self.redis.set('pumpcall',status['PC'])
        self.redis.set('pumpon',status['P'])
        self.redis.set('northcall',status['NC'])
        self.redis.set('northon',status['N'])
        self.redis.set('southcall',status['SC'])
        self.redis.set('sourthon',status['S'])
        self.redis.set('ditch',status['Ditch'])
        self.redis.set('sump',status['Sump'])
        self.redis.set('ditch_inches',self.loggr.ditchInches(status['Ditch']))
        self.redis.set('sump_inches',self.loggr.sumpInches(status['Sump']))

        if status['P'] != '0':
            self.dbLogInterval = 5
        else:
            self.dbLogInterval = 60


    def logRunningTime(self):
        startTime = time.strftime("%a, %d %b %Y %H:%M:%S -0007", self.startTime)
        currTime = time.gmtime()
        totalJobs = self.mgr.getJobCount()
        self.logprint('Spice Server running since ' + startTime + ". Total Jobs:%d" % totalJobs)

    def setLogFile(self,fname):
        self.logfile = fname
        self.logfp = open(self.logfile,'w')

    def logprint(self,txt):

        self.processLogMessages()
        self.lprint(txt)

    def lprint(self, txt):

        currTime = localtime()
        logTime = strftime("%Y%m%d %H:%M:%S", currTime)
        txt = logTime + " " + txt
        self.printlock.acquire()
        if self.logfp:
            self.logfp.write(txt)
            if txt[-1] != '\n':
                self.logfp.write("\n")
            self.logfp.flush()
        else:
            sys.stdout.write(txt)
            if txt[-1] != '\n':
                sys.stdout.write("\n")
            sys.stdout.flush()

        self.printlock.release()

    def shutdown(self):
        self.logprint("Shutting down..")

        self.logprint("Done")
        if self.logfp:
            self.logfp.close()

    def onShutdown(self):

        self.logprint("Received the shutdown signal!")
        self.enRun = False

    def setDaemon(self,bEnable):
        """
        Enable the isDaemon flag.
        """

        self.isDaemon = bEnable

    def getDebug(self):
        return self._debug

    def setDebug(self,db):
        self._debug = db

    debug = property(getDebug,setDebug)


    def processLogMessages(self):
        """

        Check the log fields, write to the log file

        Acquire the lock, then check if any of the text log values
        have changed. If they have, then update the GUI elements
        and clear the 'changed' variables.

        Release the lock.

        """
        self.msglock.acquire()

        if self.txtChanged:
            self.txtChanged = False
            self.lprint("Msg:"+self.txt)
            self.txt = ""

        self.msglock.release()

    def processMessages(self):
        """
        Sim messages for this server are placed into our server message queue.
        Pop messages from the queue and pass them along to any sims.
        """

        msgq = 'msg:%s' % self.myid

        jmsg = self.rpop(msgq)
        while jmsg:
            msg = json.loads(jmsg)
            simid = msg['simid']
            cmd = msg['cmd']

            sim = self.getSim(simid)

            if sim:
                sim.ping()

                if cmd == 'status':
                    pass # nothing to do
                elif cmd == 'cancel':
                    # cancel this sim!
                    self.logprint("Processing message. Simid:%s cmd:%s." % (simid,cmd))
                    self.simCancel(sim)
                elif cmd == 'removed':
                    # sim removed by client
                    self.logprint("Processing message. Simid:%s cmd:%s." % (simid,cmd))
                    self.mgr.removeSim(sim)
                elif cmd == 'data':
                    # Sim data has been retrieved by client.
                    pass
                else:
                    print("Unknown command:%s for simID:%s." % (cmd,simid))

            jmsg = self.rpop(msgq)


def start_server():
    """ Start the server.

    Create a sim manager and a redis manager, and connect the two together..
    then start the redis manager running.

    """
    parser = argparse.ArgumentParser()

    parser.add_argument("--host",default='127.0.0.1')

    parser.add_argument("--port",type=int,default=6388)

    parser.add_argument("--db",type=int,default=0)

    parser.add_argument("--debug",action="store_true")

    args = parser.parse_args()

    host = args.host

    redismgr = DitchManager(host,args.port, args.db)
    redismgr.debug = args.debug == True
    redismgr.start()
    redismgr.run()

if __name__ == "__main__":
    start_server()
