#!/usr/bin/env python

__author__ = 'kutenai'


import argparse
import time
from IrrigationAPIAT import IrrigationAPI

class DitchControl(object):
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
        self.api = IrrigationAPI()
        
def showLevels(api):
	sensors = api.getSensors()
	if sensors:
		print ("Sensor Levels: Ditch:%s Sump%s" % (sensors['ditch'],sensors['sump']))


def main():
    """
    Parse command line arguments.
    If the server is looping, or running for a continuous time, then
    enter a loop and keep calling the check function.

    """

    parser = argparse.ArgumentParser()

    parser.add_argument('--pump', help="Turn the pump on or off")

    parser.add_argument('--north', help="Turn the north valve on or off")

    parser.add_argument('--south', help="Turn the south valve on or off")

    parser.add_argument('--status', action='store_true',help="Read the status")

    parser.add_argument('--levels', action='store_true',help="Read the status")

    parser.add_argument('--loop', action='store_true',help="Read Constantly")

    args = parser.parse_args()

    api = IrrigationAPI()

    bStatus = False # Read if any of the contols are set

    if args.north and args.north in ['on','off']:
        api.northEnable(args.north == 'on')
        s = api.isNorthOn()
        print("North Array status %s and %s" % (s['call'],s['actual']))
        bStatus = True

    if args.south and args.south in ['on','off']:
        api.southEnable(args.south == 'on')
        s = api.isSouthOn()
        print("South Array status %s and %s" % (s['call'],s['actual']))
        bStatus = True

    if args.pump and args.pump in ['on','off']:
        api.pumpEnable(args.pump == 'on')
        s = api.isPumpOn()
        print("Pump status %s and %s" % (s['call'],s['actual']))
        bStatus = True

    if (bStatus or args.status):
	    stat = api.getSystemStatus()
	    if stat:
			print ("System Status:")
			for key in sorted(stat.iterkeys()):
				print ("%s => %s" % (key,stat[key]))

    if args.levels:
    	showLevels(api)
    	
    if args.loop and args.levels:
		while True:
			try:
				time.sleep(0.5)
				showLevels(api)
			except KeyboardInterrupt:
				break
			



if __name__ == "__main__":
    main()
