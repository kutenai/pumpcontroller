#!/usr/bin/env Python

import argparse
import sys
import os
import time

from signal import SIGTERM,SIGUSR1
from Ditch.DitchManager import DitchManager

from daemon import Daemon

class DitchDaemon(Daemon):

    def __init__(self,pidfile,stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        super(DitchDaemon,self).__init__(pidfile,stdin,stdout,stderr)
        self.host = '127.0.0.1'
        self.port = 6388
        self.db = 0
        self.instanceid = None


    def setHost(self,host):
        self.host = host

    def setPort(self,port):
        self.port = port

    def setDB(self,db):
        self.db = db

    def setInstanceId(self,id):
        self.instanceid = id

    def _logfile(self):
        """
        Determine the log file to used, based on permissions
        """
        # If there are multiple instances of the server, use different logs.
        if os.access("/var/log", os.W_OK):
            logroot = "/var/log"
        else:
            logroot = "/tmp"

        if self.instanceid:
            pid = os.getpid()
            logfile = os.path.join(logroot,"ditchd_%d.log" % pid)
        else:
            logfile = os.path.join(logroot,"ditchd.log")

        return logfile


    def run(self):

        # Create a manager, and a GUI. Then, cross connect them.
        # Manager will dump messages and status to the GUI, and then
        # the GUI can control the manager.
        # The gui will update the # of workers upon startup.

        app = DitchManager()
        app.setDaemon(True)

        logfile = self._logfile()
        app.setLogFile(logfile)

        app.run()

        # Not sure what this will do.. but, should probably do something.
        app.shutdown()

    def stop(self,graceful=False):
        """
          Stop the daemon
          """
        # Get the pid from the pidfile

        if graceful:
            try:
                pf = file(self.pidfile, 'r')
                pid = int(pf.read().strip())
                pf.close()
            except IOError:
                pid = None

            if not pid:
                message = "pidfile %s does not exist. Daemon not running?\n"
                sys.stderr.write(message % self.pidfile)
                return # not an error in a restart

            # Try killing the daemon process
            try:
                while 1:
                    os.kill(pid, SIGUSR1)
                    time.sleep(0.1)
            except OSError, err:
                err = str(err)
                if err.find("No such process") > 0:
                    if os.path.exists(self.pidfile):
                        os.remove(self.pidfile)
                else:
                    print str(err)
                    sys.exit(1)
        else:
            super(DitchDaemon,self).stop()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="ditchd")

    parser.add_argument("--instance")

    parser.add_argument("--host")

    parser.add_argument("--graceful",'-g', action="store_true")

    parser.add_argument("--port",type=int,default=6379)

    parser.add_argument("--db",type=int,default=0)

    parser.add_argument("command",
        choices = ['start','stop','restart','status'],
        help="Enter the command to pass to the spice daemon.")

    args = parser.parse_args()

    if os.path.exists("/var/run") and os.access("/var/run",os.W_OK):
        piddir = "/var/run"
    else:
        piddir = "/tmp"

    pidfile = os.path.join(piddir,"ditchd.pid")
    daemon = DitchDaemon(pidfile)

    if args.host:
        daemon.setHost(args.host)

    if args.port:
        daemon.setPort(args.port)

    if args.db:
        daemon.setDB(args.db)

    if 'start' == args.command:
        daemon.start()
    elif 'stop' == args.command:
        daemon.stop(args.graceful)
    elif 'restart' == args.command:
        daemon.restart()
    elif 'status' == args.command:
        daemon.status()
    else:
        print "Unknown command:%s" % args.command
        sys.exit(2)

    # Exit. The Daemon will be doing what it does..
    sys.exit(0)
