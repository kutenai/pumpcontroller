#!/usr/bin/env python

import argparse

from Ditch.DitchManager import DitchManager

def runTests():

    mgr = DitchManager('localhost', 6388, 9)

    # Test Alarms

    mgr.alarmChecks(11)
    mgr.alarmChecks(12)
    mgr.alarmChecks(13)
    mgr.alarmChecks(13.2)
    mgr.alarmChecks(13)
    mgr.alarmChecks(12.5)
    mgr.alarmChecks(14)
    mgr.alarmChecks(12)

def start_server():
    """ Start the server.

    Create a ditch manager and a redis manager, and connect the two together..
    then start the redis manager running.

    """
    parser = argparse.ArgumentParser()

    parser.add_argument("--host",default='127.0.0.1')

    parser.add_argument("--port",type=int,default=6388)

    parser.add_argument("--db",type=int,default=0)

    parser.add_argument("--debug",action="store_true")

    parser.add_argument("--test", action='store_true', help="Enter test mode")

    args = parser.parse_args()

    if args.test:
        runTests()

    host = args.host

    redismgr = DitchManager(host,args.port, args.db)
    redismgr.debug = args.debug == True
    redismgr.start()
    redismgr.run()

if __name__ == "__main__":
    start_server()

