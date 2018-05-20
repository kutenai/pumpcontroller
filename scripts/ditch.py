#!/usr/bin/env python

import argparse
import time

from Ditch.Controller import DitchController

def main():
    """
    Parse command line arguments.
    If the server is looping, or running for a continuous time, then
    enter a loop and keep calling the check function.

    """

    print("Here")

    parser = argparse.ArgumentParser()

    parser.add_argument('--pump', '-p', help="Turn the pump on or off")

    parser.add_argument('--runnorth', action="store_true", help="Run the north zone.")

    parser.add_argument('--runsouth', action="store_true", help="Run the south zone.")

    parser.add_argument('--off', '-o', action="store_true", help="Turn all off.")

    parser.add_argument('--north','-n', help="Turn the north valve on or off")

    parser.add_argument('--south', '-s',help="Turn the south valve on or off")

    parser.add_argument('--status', '-t', action='store_true', help="Read the status")

    parser.add_argument('--levels', '-l', action='store_true', help="Read the status")

    parser.add_argument('--loop', action='store_true', help="Read Constantly")

    args = parser.parse_args()

    ctrl = DitchController()

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
