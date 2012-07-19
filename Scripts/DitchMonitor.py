__author__ = 'kutenai'

import smtplib
from email.MIMEText import MIMEText
import json
import redis
from redis.exceptions import (
    ConnectionError,
    )
import optparse
import os
import glob
import re
import sys
from time import time,sleep,localtime,strftime
import IrrigationAPI
from DBConnection import DBConnection
from DBDitch import *

class DitchMonitor(object):
    """
    Ditch Monitor runs continuously on the server.

    The Monitor performs the following checks
    - Log the ditch and sump levels.
    - turn off the pump, and both valves if the water level is too low.
    - apply any rules to turn ON the values..

    The Monitor will report issues via e-mail. A follow-up e-mail
    is sent every 15 minutes. If the error list changes, a new
    e-mail is sent.

    """

    def __init__(self,host,port):

        self.host = host
        self.port = port
        self.redis = redis.StrictRedis(host=host, port=6379, db=0)

        self.errors = []
        self.isOkay = True

        self.username = "henderson.ed@gmail.com"
        self.password = "doulos56"
        self.smtpserver = "smtp.gmail.com:587"
        self.reportdest = 'kutena@me.com'
        self.tmpdir = "/tmp"

        self.resendRate = 15*60

        self.api = IrrigationAPI.IrrigationAPI()
        self.api.initHardware()

        self.conn = DBConnection('local')
        self.db = DBDitch(self.conn)

    def checkRedis(self):
        """
        Perform  check on the redist server. If it is not working, send an
        urgent e-mail and exit. We can do nothing without a working redis
        server.
        """

        try:
            self.redis.set('DitchredisCheck',0)
        except:
            # Redis is not working!
            subject = "DitchMonitor: Redis Database not responding!"
            message = """
The Redis database at host=%s and port=%d is not responding.
DitchMonitor will exit and restart again in one minute.
            """ % (self.host, self.port)
            self.sendMessage(subject,message)
            sys.exit(2)


    def addError(self,errmsg):

        self.errors.append(errmsg)

    def getErrorString(self):
        """
        Assemble the list of errors into a string.
        Clear the current error list.
        """
        msg = "\n".join(self.errors)
        self.errors=  []
        return msg

    def reportUpdate(self):
        """
        Send an e-mail reporting the current status.

        IF new errors are detected, send an e-mail. Record the
        current error string with Redis. If the string changes,
        send an update.

        If the string is the same, send a follow-up every 15 minutes.

        If errors are cleared, send a followup that indicates all is
         well.
        """

        message = self.getErrorString()
        previousMessage = self.redis.get('DitchPreviousMessage')


        if previousMessage == "" and message != "":
            # New errors.
            subject = "DitchMonitor Monitor Errors Detected."
            self.redis.set('DitchPreviousMessage',message)
            self.redis.set('DitchPreviousMessageTime',time())
            self.sendMessage(subject,message)
        elif previousMessage != "" and message == "":
            # Errors fixed..
            subject = "DitchMonitor: Server back to Normal."
            self.redis.set('DitchPreviousMessage',message)
            self.redis.set('DitchPreviousMessageTime',time())
            self.sendMessage(subject,message)
        elif previousMessage != message:
            # Changed Errors
            subject = "DitchMonitor Monitor New Errors Detected."
            self.redis.set('DitchPreviousMessage',message)
            self.redis.set('DitchPreviousMessageTime',time())
            self.sendMessage(subject,message)
        else:
            # Previous message == message
            previousTime = self.redis.get('DitchPreviousMessageTime')
            try:
                previousTime = float(previousTime)
            except:
                self.redis.set('DitchPreviousMessageTime',time())
                previousTime = time()

            if time() - previousTime > self.resendRate:
                self.redis.set('DitchPreviousMessageTime',time())
                subject = "DitchMonitor Errors (resent on %s)" \
                    % strftime("%m-%d-%Y at %H:%M",localtime())
                self.sendMessage(subject,message)

    def sendMessage(self,subject,message):
        """
        Send an e-mail message to the given recipient(s)
        """

        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = self.username
        msg['To'] = self.reportdest

        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(self.username,self.password)
        server.sendmail(self.username, [self.reportdest], msg.as_string())
        server.quit()

    def statusPrint(self):
        """
        Print the status of the ditch.

        """

        r = self.redis

    def isPumpOn(self):

        if self.redis.get("Ditch_pumpOn") == '1':
            return True
        else:
            return False

    def setPump(self,bOn):

        if bOn and self.sump > 200:
            self.api.pumpEnable(True)
            self.redis.set("Ditch_pumpOn","1")
            print ("Pump turned on")
        else:
            self.api.pumpEnable(False)
            self.redis.set("Ditch_pumpOn","0")
            print ("Pump turned off")

    def setNorthZone(self,bOn):

        if bOn and self.isPumpOn():
            self.api.northZoneEnable(True)
            self.redis.set("Ditch_northZoneOn","1")
            print ("North zone on")
        else:
            self.api.northZoneEnable(False)
            self.redis.set("Ditch_northZoneOn","0")
            print ("North zone off")

    def setSouthZone(self,bOn):

        if bOn and self.isPumpOn():
            self.api.southZoneEnable(True)
            self.redis.set("Ditch_southZoneOn","1")
            print ("South zone on")
        else:
            self.api.southZoneEnable(False)
            self.redis.set("Ditch_southZoneOn","0")
            print ("South zone off")

    def setLevels(self,ditch,sump):

        self.ditch = ditch
        self.sump = sump

        if self.sump < 300:
            self.sumpLow = True
        else:
            self.sumpLow = False

        self.ditchHasWater = False
        self.ditchClogged = False

        if self.ditch < 200:
            self.ditchClogged = True
        elif ditch < 400:
            self.ditchHasWater = True

    def levelChecks(self):

        if self.sumpLow and self.isPumpOn():

            print("Sump Low!!!!")
            self.setPump(False)
            self.setNorthZone(False)
            self.setSouthZone(False)


    def logDitchLevels(self):

        s = self.api.getSensorData()
        if s:
            ditch = s['sensor1']
            sump = s['sensor2']

            self.setLevels(int(ditch),int(sump))

            print ("Logged Ditch Values Ditch:%d Sump:%d"
                % (int(ditch), int(sump)))

            self.db.insertLogEntry(int(ditch),int(sump),0)
        else:
            print("Log failed to get sensor data!!")

    def callCheck(self):
        """
        I need some additional firmware functions:
        - status of pump, valve1 and valve2
        - code that turns off valves if the pump is off, this way
          the valves can just be left 'on'
        - a pump 'call' that says "turn on the pump if there is enough water"

        """

        if self.sumpLow:
            return

        if not self.ditchHasWater:
            return

        pumpCall = self.redis.get("Ditch_pumpCall")
        northZoneCall = self.redis.get("Ditch_northZoneCall")
        southZoneCall = self.redis.get("Ditch_southZoneCall")

        if pumpCall == '1':
            if northZoneCall == '1':
                self.setPump(True)
                self.setNorthZone(True)
            else:
                self.setNorthZone(False)

            if southZoneCall == '1':
                self.setPump(True)
                self.setSouthZone(True)
            else:
                self.setSouthZone(False)
        else:
            self.setSouthZone(False)
            self.setNorthZone(False)
            self.setPump(False)

    def runChecks(self):
        """
        Check all servers to insure they are all
        up-to-date on their pings.

        Run through the various checks. Report any updates via e-mail.
        """

        self.checkRedis()
        self.logDitchLevels()
        self.levelChecks()
        self.callCheck()

def main():
    """
    Parse command line arguments.
    If the server is looping, or running for a continuous time, then
    enter a loop and keep calling the check function.

    """

    usage = "usage: %prog "
    parser = optparse.OptionParser(usage)
    parser.add_option("--remote",
        action="store_true",
        dest="remote",
        default=False
    )
    parser.add_option("--host",
        action="store",
        type="string",
        dest="host",
        default='127.0.0.1'
    )

    parser.add_option("-s", "--sleeptime",
        action="store",
        type="int",
        dest="sleeptime",
        default=60)

    parser.add_option("-l", "--loop",
        action="store_true", dest="loop",
        help="Loop forever.")

    parser.add_option("-n", "--nloops",
        action="store", dest="nloops",
        type="int",
        help="Loop n times.")

    parser.add_option("-d", "--duration",
        action="store", dest="duration",
        type="int", help="Loop for N seconds.")

    (options, args) = parser.parse_args()

    if options.remote:
        host = 'partsim.eeweb.com'
    else:
        host = options.host


    mon = DitchMonitor(host, 6379)

    if options.loop:
        while True:
            mon.runChecks()
            sleep(options.sleeptime)
    elif options.nloops:
        loopCount = options.nloops
        while loopCount:
            mon.runChecks()
            sleep(options.sleeptime)
            loopCount -= 1
    elif options.duration:
        loopStartTime = time()
        runTime = 0
        mon.runChecks()
        mon.callCheck()
        while runTime < options.duration:
            sleep(options.sleeptime)
            mon.runChecks()
            runTime = time()-loopStartTime+options.sleeptime
    else:
        # One time.
        print("One time execution.")
        mon.runChecks()


if __name__ == "__main__":
    main()
