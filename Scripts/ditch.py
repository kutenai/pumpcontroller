#!/usr/bin/env python

__author__ = 'kutenai'

import argparse
import time
from DitchRedisHandler import DitchRedisHandler


class Ditch(DitchRedisHandler):
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
        super(Ditch, self).__init__('localhost', 6388, 0)
        self.hi = True
        self.redisConnect()

    def setRequest(self,key,val):

        req = key + 'request'
        if val:
            self.redis.set(req,1)
            print ("Set %s to 1" % req)
        else:
            self.redis.set(req,0)
            print ("Set %s to 0" % req)

    def allOff(self):
        print("Setting all controls to off.")
        self.setRequest('pump',False)
        self.setRequest('north',False)
        self.setRequest('south',False)

    def runNorth(self):
        print("Turning on North Zone.")
        self.setRequest('pump',True)
        self.setRequest('north',True)
        self.setRequest('south',False)


    def runSouth(self):
        print("Turning on South Zone.")
        self.setRequest('pump',True)
        self.setRequest('north',True)
        self.setRequest('south',False)


    def southEnable(self, bOn):
        if bOn:
            self.setRequest('south', True)
        else:
            self.setRequest('south', False)


    def pumpEnable(self, bOn):
        if bOn:
            self.setRequest('pump', True)
        else:
            self.setRequest('pump', False)


    def northEnable(self, bOn):
        if bOn:
            self.setRequest('north', True)
        else:
            self.setRequest('north', False)


    def southEnable(self, bOn):
        if bOn:
            self.setRequest('south', True)
        else:
            self.setRequest('south', False)


    def isPumpOn(self):
        return self.redis.get('pumpon') != '0'


    def isNorthOn(self):
        return self.redis.get('northon') != '0'


    def isSouthOn(self):
        return self.redis.get('southon') != '0'


    def showLevels(self):
        d = self.redis.get('ditch')
        s = self.redis.get('sump')
        di = self.redis.get('ditch_inches')
        si = self.redis.get('sump_inches')

        print("Ditch is %s\" (%d)" % (di, int(d)))
        print("Sump is %s\" (%d)" % (si, int(s)))


    def getSystemValue(self, key, default):
        val = self.redis.get(key)
        if val == None:
            val = default
            self.lprint("Setting %s to default value of %s" % (key,default))
            self.redis.set(key, val)

        return val


    def getSystemStatus(self):
        stat = {
            'ditch': self.getSystemValue('ditch', 0),
            'sump': self.getSystemValue('sump', 0),
            'ditch_in': self.getSystemValue('ditch_inches', 0.0),
            'sump_in': self.getSystemValue('sump_inches', 0.0),
            'pumpcall': self.getSystemValue('pumpcall', 0),
            'northcall': self.getSystemValue('northcall', 0),
            'southcall': self.getSystemValue('southcall', 0),
            'pumpon': self.getSystemValue('pumpon', 0),
            'northon': self.getSystemValue('northon', 0),
            'southon': self.getSystemValue('southon', 0)
        }
        return stat


    def showSystemStatus(self):
        print("Showing System Status:")
        stat = self.getSystemStatus()

        print("Pump: Call:%s On:%s" % (stat['pumpcall'], stat['pumpon']))
        print("North: Call:%s On:%s" % (stat['northcall'], stat['northon']))
        print("South: Call:%s On:%s" % (stat['southcall'], stat['southon']))
        print("Ditch: %s\" (%d)" % (stat['ditch_in'], int(stat['ditch'])))
        print("Sump: %s\" (%d)" % (stat['sump_in'], int(stat['sump'])))


    def lprint(self, string):
        print(string)


def main():
    """
    Parse command line arguments.
    If the server is looping, or running for a continuous time, then
    enter a loop and keep calling the check function.

    """

    parser = argparse.ArgumentParser()

    parser.add_argument('--pump', help="Turn the pump on or off")

    parser.add_argument('--runnorth', action="store_true", help="Run the north zone.")

    parser.add_argument('--runsouth', action="store_true", help="Run the south zone.")

    parser.add_argument('--off', action="store_true", help="Turn all off.")

    parser.add_argument('--north', help="Turn the north valve on or off")

    parser.add_argument('--south', help="Turn the south valve on or off")

    parser.add_argument('--status', action='store_true', help="Read the status")

    parser.add_argument('--levels', action='store_true', help="Read the status")

    parser.add_argument('--loop', action='store_true', help="Read Constantly")

    args = parser.parse_args()

    ctrl = Ditch()

    bStatus = False # Read if any of the controls are set

    if args.runnorth:
        ctrl.runNorth()

    if args.runsouth:
        ctrl.runSouth()

    if args.off:
        ctrl.allOff()

    if args.north and args.north in ['on', 'off']:
        ctrl.northEnable(args.north == 'on')
        s = ctrl.isNorthOn()
        print("North Array status %s" % s)
        bStatus = True

    if args.south and args.south in ['on', 'off']:
        ctrl.southEnable(args.south == 'on')
        s = ctrl.isSouthOn()
        print("South Array status %s" % s)
        bStatus = True

    if args.pump and args.pump in ['on', 'off']:
        ctrl.pumpEnable(args.pump == 'on')
        s = ctrl.isPumpOn()
        print("Pump status %s" % s)
        bStatus = True

    if (bStatus or args.status):
        stat = ctrl.showSystemStatus()

    if args.levels:
        ctrl.showLevels()

    if args.loop and args.levels:
        while True:
            try:
                time.sleep(5)
                ctrl.showLevels()
            except KeyboardInterrupt:
                break

    ctrl.showSystemStatus()


if __name__ == "__main__":
    main()
