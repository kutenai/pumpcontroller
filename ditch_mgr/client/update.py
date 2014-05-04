#!/usr/bin/env python

import time

from celery import group,chain

from mgr.tasks import status
from gbmgr.tasks import onstatus

if __name__ == "__main__":

    s = status.apply_async()

    while not s.ready():
        #print("Waiting for finallity..")
        time.sleep(0.100)

    onstatus.delay(s.get())

    #print("Main dealio is done..")
