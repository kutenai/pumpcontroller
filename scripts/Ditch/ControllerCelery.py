#!/usr/bin/env python

import sys
import json

from celery import Celery,group,chain

sys.path.append('/Users/kutenai/proj/bondiproj/pumpcontrol/ditch_mgr')

from mgr.tasks import pump_enable, south_enable, north_enable, status

class DitchController(object):
    """
    Ditch Logger runs one time, reads the sensor levels, and logs
    them to the COSM site.



    The Monitor performs the following checks
    - Log the ditch and sump levels.
    - turn off the pump, and both valves if the water level is too low.
    - apply any rules to turn ON the values..

    The Monitor will report issues via e-mail. A follow-up e-mail
    is sent every 15 minutes. If the error list changes, a new
    e-mail is sent.

    """

    def __init__(self):
        self.hi = True

    def allOff(self):
        print("Setting all controls to off.")
        pump_enable.delay(False).get()
        south_enable.delay(False).get()
        north_enable.delay(False).get()

    def runNorth(self):
        print("Turning on North Zone.")
        chain(
            south_enable(False) |
            north_enable(True) |
            pump_enable(True)
        )()


    def runSouth(self):
        print("Turning on South Zone.")
        chain(
            south_enable(True) |
            north_enable(False) |
            pump_enable(True)
        )()


    def southEnable(self, bOn):
        south_enable.delay(bOn)


    def pumpEnable(self, bOn):
        pump_enable.delay(bOn)


    def northEnable(self, bOn):
        north_enable.delay(bOn)


    def isPumpOn(self):
        #return self.redis.get('pumpon') != '0'
        return False


    def isNorthOn(self):
        #return self.redis.get('northon') != '0'
        return False


    def isSouthOn(self):
        #return self.redis.get('southon') != '0'
        return False


    def showLevels(self):
        print("Not Implemented")


    def getSystemValue(self, key, default):
        stat = status.delay().get()


    def getSystemStatus(self):
        stat = status.delay().get()
        return json.loads(stat)


    def showSystemStatus(self):
        print("Showing System Status:")
        stat = self.getSystemStatus()

        print("Pump: Call:%s On:%s" % (stat['PC'], stat['P']))
        print("North: Call:%s On:%s" % (stat['NC'], stat['N']))
        print("South: Call:%s On:%s" % (stat['SC'], stat['S']))
        print("Ditch: %s\" (%d)" % ("?", int(stat['Ditch'])))
        print("Sump: %s\" (%d)" % ("?", int(stat['Sump'])))


    def lprint(self, string):
        print(string)
