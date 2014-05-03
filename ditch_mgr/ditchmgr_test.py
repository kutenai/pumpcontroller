#!/usr/bin/env python

import sys
from os.path import abspath
from unipath import Path

BASE_PATH = Path(abspath(__file__)).ancestor(1)
SCRIPT_PATH = BASE_PATH.ancestor(1).child('scripts')
print("BasePath:%s" % BASE_PATH)


sys.path.append(SCRIPT_PATH)
print("Appended script path:%s" % SCRIPT_PATH)

from celery import Celery

from Ditch.IrrigationAPI import IrrigationAPI

app = Celery('ditch_tasks', broker='redis://gardenbuzz.com:6379/0')
api = IrrigationAPI()

@app.task
def status():
    stat = api.getSystemStatus()
    return stat

@app.task
def read_sensors():
    d = api.getSensorData()
    return d

@app.task
def pump_enable(bEnable):
    api.pumpEnable(bEnable)

@app.task
def south_enable(bEnable):
    api.southZoneEnable(bEnable)

@app.task
def north_enable(bEnable):
    api.northZoneEnable(bEnable)


if __name__ == "__main__":
    app.worker_main()
