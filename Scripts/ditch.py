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
        super(DitchControl,self).__init__('localhost',6388,0)
        self.hi = True
        self.redisConnect()
        
        
    def allOff(self):
		self.redis.set('northrequest','0')
		self.redis.set('southrequest','0')
		self.redis.set('pumprequest','0')

    def runNorth(self):

		self.redis.set('northrequest','1')
		self.redis.set('southrequest','0')
		self.redis.set('pumprequest','1')
 
    def runSouth(self):
		self.redis.set('northrequest','0')
		self.redis.set('southrequest','1')
		self.redis.set('pumprequest','1')

    def southEnable(self,bOn):

        if bOn:
            self.redis.set('southrequest','1')
        else:
            self.redis.set('southrequest','0')

    def pumpEnable(self,bOn):

        if bOn:
            self.redis.set('pumprequest','1')
        else:
            self.redis.set('pumprequest','0')

    def northEnable(self,bOn):

        if bOn:
            self.redis.set('northrequest','1')
        else:
            self.redis.set('northrequest','0')

    def southEnable(self,bOn):

        if bOn:
            self.redis.set('southrequest','1')
        else:
            self.redis.set('southrequest','0')

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

        print("Ditch is %s\" (%d)" % (di,int(d)))
        print("Sump is %s\" (%d)" % (si,int(s)))

    def showSystemStatus(self):

        print("Showing System Status:")
        d = self.redis.get('ditch')
        s = self.redis.get('sump')
        pc = self.redis.get('pumpcall')
        p = self.redis.get('pumpon')
        nc = self.redis.get('northcall')
        n = self.redis.get('northon')
        sc = self.redis.get('southcall')
        s = self.redis.get('southon')

        print("Pump: Call:%s On:%s" %(pc,p))
        print("North: Call:%s On:%s" %(nc,n))
        print("South: Call:%s On:%s" %(sc,s))
        print("Ditch: %s\" (%d)" %(self.redis.get('ditch_inches'),int(self.redis.get('ditch'))))
        print("Sump: %s\" (%d)" %(self.redis.get('sump_inches'),int(self.redis.get('sump'))))

    def lprint(self,str):
        print(str)


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

    parser.add_argument('--status', action='store_true',help="Read the status")

    parser.add_argument('--levels', action='store_true',help="Read the status")

    parser.add_argument('--loop', action='store_true',help="Read Constantly")

    args = parser.parse_args()

    ctrl = DitchControl()

    bStatus = False # Read if any of the contols are set
    
    if args.runnorth:
    	ctrl.runNorth()
    	
    if args.runsouth:
    	ctrl.runSouth()
    	
    if args.off:
    	ctrl.allOff()

    if args.north and args.north in ['on','off']:
        ctrl.northEnable(args.north == 'on')
        s = ctrl.isNorthOn()
        print("North Array status %s" % s)
        bStatus = True

    if args.south and args.south in ['on','off']:
        ctrl.southEnable(args.south == 'on')
        s = ctrl.isSouthOn()
        print("South Array status %s" % s)
        bStatus = True

    if args.pump and args.pump in ['on','off']:
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




if __name__ == "__main__":
    main()
