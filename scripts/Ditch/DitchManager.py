from __future__ import absolute_import

from threading import RLock
import os,atexit

from time import time,localtime,gmtime,strftime,sleep
import signal
import sys
import argparse

from .DitchRedisHandler import DitchRedisHandler

from .IrrigationAPIAT import IrrigationAPI
from .DitchLogger import DitchLogger
from .DitchMessenger import DitchMessenger

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

        self.messenger = DitchMessenger()
        self.messenger.setPrintObj(self)

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

        self.systemStates = {
            'pump' : 'off',
            'north' : 'off',
            'south' : 'off'
        }

        self.currCommandValues = {
            'pump' : False,
            'north' : False,
            'south' : False
        }

        self.alarms = {
            'ditch' : {
                'alarm' : 13.0,
                'warm' : 12.5,
                'normal' : 12.0,
                'alarmStarted' : None,
                'lastMsgSent' : None,
                'alarmed' : False
            }
        }

        self.logIntervals = {
            'on' : {
                'cosm' : 10,
                'db' : 5
            },
            'off' : {
                'cosm' : 60,
                'db'   : 60
            }
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
            # Wait for the run flag to be cleared

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

        self.lastStatusUpdate = time()
        self.statusUpdateRate = 5 # Every 5 seconds.

        while self.enRun:
            try:
                if not self.isConnected:
                    sleep(5) # Retry at 5 second intervals
                    self.redisConnect()
                    continue # Jump back to the top while loop

                self.checkCommandValues()

                if time() - self.lastStatusUpdate > self.statusUpdateRate:
                    self.updateStatus()

                # Do some things
                self.logCurrentLevels()

                # Do maintenance in between actions
                self.processLogMessages()
            except Exception as e:
                self.lprint("Exception occurred: %s" % e)

            sleep(0.5)


        self.redisDisconnect()

    def getSystemValue(self, key, default):
        val = self.redis.get(key)
        if val == None:
            val = default
            self.lprint("Set %s to default of %s" % (key,default))
            self.redis.set(key, val)

        return val

    def initRedisValues(self):
        """
        Read the redis values. Initialize them if they don't exist,
        and store our copies if they do.
        """

        pRequest = self.getSystemValue('pumprequest','0')
        nRequest= self.getSystemValue('northrequest','0')
        sRequest= self.getSystemValue('southrequest','0')

        self.currCommandValues['pump'] = pRequest != '0'
        self.currCommandValues['north'] = nRequest  != '0'
        self.currCommandValues['south'] = sRequest  != '0'

        for key in ['pump','north','south']:
            self.api.sendBool(key,self.currCommandValues[key])
            self.lprint("%s set to %s" % (key,self.currCommandValues[key]))


    def checkCommandValues(self):
        """
        Determine if any of the redis command values have changed.

        If so, then send the appropriate commands

        """

        pRequest = self.redis.get('pumprequest')
        nRequest= self.redis.get('northrequest')
        sRequest= self.redis.get('southrequest')

        cmds = {
            'pump'  : pRequest != '0',
            'north' : nRequest != '0',
            'south' : sRequest != '0'
        }

        bUpdateStatus = False
        for key in cmds.iterkeys():
            if cmds[key] != self.currCommandValues[key]:
                try:
                    self.api.sendBool(key,cmds[key])
                    self.lprint("%s set to %s" % (key,cmds[key]))
                    self.currCommandValues[key] = cmds[key]
                    bUpdateStatus = True

                except Exception as e:
                    self.lprint("Exception trying to set the command value %s to %s." % (key,cmds[key]))

        if bUpdateStatus:
            self.updateStatus()

    def logCurrentLevels(self):
        """
        Query the levels from the Ditch Unit, and log them.
        """

        dbDiff = time() - self.lastDBLogTime
        cosmDiff = time() - self.lastCosmLogTime

        if dbDiff > self.dbLogInterval or cosmDiff > self.cosmLogInterval:

            self.alarmChecks(self.loggr.ditchInches(self.redis.get('ditch')))

            ditch = self.redis.get('ditch')
            sump = self.redis.get('sump')
            pump = self.redis.get('pumpon')
            north = self.redis.get('northon')
            south = self.redis.get('southon')

            if cosmDiff > self.cosmLogInterval:
                self.lastCosmLogTime = time()
                self.loggr.logResultsCosm(ditch,sump)
            if dbDiff > self.dbLogInterval:
                self.lastDBLogTime = time()
                self.loggr.logResultsDB(ditch,sump,pump,north,south)


    def inAlarmState(self,ditchInches):
        """
        Provide some hysteresis for the alarm.
        If we are not in an alarmed state, and the level goes above the alarm level,
        then send the alarm.

        If we are in the alarmed state, then the level must drop 1" below the alarm level
        to clear the alarm.
        """

        a = self.alarms['ditch']

        if a['alarmed']:
            # If we are in an alarm state, then the value has to drop 1" below that state.
            if ditchInches > (a['alarm'] - 1):
                return True
        else:
            if ditchInches > a['alarm']:
                return True

        return False


    def alarmChecks(self,ditchInches):
        """
        Check for alarm levels.

        If the ditch level gets too high, then we send an alarm.
        A high "full" flow gives a ditch level of 11.4", perhaps as high as 12".  A clogged ditch
        will be at 16.85" - I know!
        """

        a = self.alarms['ditch']

        tnow = time()
        if self.inAlarmState(ditchInches):

            if not a['alarmed']:
                # First time we detected an alarm
                self.sendAlarmMessage(ditchInches, tnow, tnow, 0)
                a['alarmed'] = True
                a['alarmStarted'] = tnow
                a['lastMsgSent'] = tnow
            else:
                # Already alarmed, should we send a reminder?
                if (tnow - a['lastMsgSent'] > 30*60): # 30 minutes
                    alarmLength = int(tnow - a['alarmStarted'])/60
                    # First time we detected an alarm
                    self.sendAlarmMessage(ditchInches, a['alarmStarted'], tnow, alarmLength)
                    a['alarmed'] = True
                    a['lastMsgSent'] = tnow
        else:
            if a['alarmed']:
                # If we are in an alarmed state, then send a 'all clear' message
                alarmLength = int(tnow - a['alarmStarted'])/60
                self.sendAlarmClearMessage(ditchInches, a['alarmStarted'], tnow, alarmLength)
                a['alarmed'] = False
                a['alarmStarted'] = None
                a['lastMsgSent'] = None


    def sendAlarmMessage(self,ditchInches, alarmStart, tnow, alarmLength):
        """
        Send an alarm message
        """
        subject = "Ditch is Clogged!"
        msg = """
    The Ditch at Ed & Vicki's house is reading a very high level.
    Levels greater than 13" usually indicate that the ditch is clogged.
    The current level is %f"

    Please take steps to clear the ditch, otherwise the property will be flooded.

    The original ditch alarm occured at %s. The time is now %s. The ditch has been flooded
    for %d minutes.

            """ % (ditchInches,
                   strftime("%A, %H:%M",localtime(alarmStart)),
                   strftime("%A, %H:%M",localtime(tnow)),
                   int(alarmLength))

        self.messenger.sendMessage('alarm',subject, msg)

    def sendAlarmClearMessage(self,ditchInches, alarmStart, tnow, alarmLength):
        """
        Send an alarm cleared message
        """
        subject = "Ditch Clog has been Cleared!"
        msg = """
    The Ditch at Ed & Vicki's house was reading a clogged state, but now the level is below
    the alarm level by at least an inch.

    Levels greater than 13" usually indicate that the ditch is clogged.
    The current level is %f"

    The original ditch alarm occured at %s. The time is now %s. The ditch has been flooded
    for %d minutes.

            """ % (ditchInches,
                   strftime("%A, %H:%M",localtime(alarmStart)),
                   strftime("%A, %H:%M",localtime(tnow)),
                   int(alarmLength))

        self.messenger.sendMessage('alarm',subject, msg)

    def updateStatus(self):
        """
        Get the current status of the system, and update the redis
        variables with all of the call and actual values.

        Update the log intervals to be slow if nothing is on.
        """

        try :
            st = self.api.getSystemStatus()

            if st:
                self.updateRedis(st)

            bFast = False
            for key in ['P','PC','N','NC','S','SC']:
                if st[key] != '0':
                    bFast = True

            if bFast:
                self.dbLogInterval = 5
                self.cosmLogInterval = 10
            else:
                self.dbLogInterval = 60
                self.cosmLogInterval = 60
        except:
            self.lprint("Exception updating status")


    def updateRedis(self,status):
        """
        Use the given status structure and upate all of the redis variables with
        the current values.
        """

        self.redis.set('pumpcall',status['PC'])
        self.redis.set('pumpon',status['P'])
        self.redis.set('northcall',status['NC'])
        self.redis.set('northon',status['N'])
        self.redis.set('southcall',status['SC'])
        self.redis.set('southon',status['S'])
        self.redis.set('ditch',status['Ditch'])
        self.redis.set('sump',status['Sump'])
        self.redis.set('ditch_inches',self.loggr.ditchInches(status['Ditch']))
        self.redis.set('sump_inches',self.loggr.sumpInches(status['Sump']))

        try:
            self.loggr.logSystemStatus(status['P'] != '0',
                                       status['N'] != '0',
                                       status['S'] != '0')

        except:
            pass


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
        if self.logfp and not self.logfp.closed:
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


