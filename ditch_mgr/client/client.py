#!/usr/bin/env python

from json import loads

from celery import Celery,group,chain

app = Celery('mgr.tasks')
app.config_from_object('mgr.celeryconfig')
from mgr.tasks import status

app2 = Celery('gbmgr.tasks')
app2.config_from_object('gbmgr.celeryconfig')
from gbmgr.tasks import onstatus

if __name__ == "__main__":

    s = status.apply_async(link=onstatus.s()).get()
    #print("Status:%s" % s)
    onstatus.delay(s).get()
    #chain( status.s() | onstatus.s() )()

    print("Main dealio is done..")
