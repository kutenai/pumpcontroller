#!/usr/bin/env python

from celery import Celery

app = Celery('mgr.tasks',
             broker='redis://gardenbuzz.com:6379/0',
             backend='redis://gardenbuzz.com:6379/1')

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

    results = s.get()

    print("Status:%s" % results)
