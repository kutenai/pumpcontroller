#!/usr/bin/env python

from celery import Celery

app = Celery('mgr.tasks')
app.config_from_object('mgr.celeryconfig')

app2 = Celery('gbmgr.tasks')
app2.config_from_object('gbmgr.celeryconfig')

@app2.task
def onstatus(d):
    """
    Handler for status results..
    :param d:
    :return:
    """
    print("Status:%s" % d)

@app.task
def status():
    pass


@app.task
def read_sensors():
    pass

@app.task
def pump_enable(bEnable):
    pass


@app.task
def south_enable(bEnable):
    pass

@app.task
def north_enable(bEnable):
    pass

if __name__ == "__main__":
    s = status.delay()

    while not s.ready():
        pass

    print("Main dealio is done..")
