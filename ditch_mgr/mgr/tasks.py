from __future__ import absolute_import

import sys
from os.path import abspath
from unipath import Path

BASE_PATH = Path(abspath(__file__)).ancestor(1)
SCRIPT_PATH = BASE_PATH.ancestor(2).child('scripts')
print("BasePath:%s" % BASE_PATH)

sys.path.append(SCRIPT_PATH)
print("Appended script path:%s" % SCRIPT_PATH)

from mgr.celery import app
from Ditch.IrrigationAPIAT import IrrigationAPI

api = IrrigationAPI()
api.Initialize()

@app.task
def status():
    print("Getting system status..")
    stat = api.getSystemStatus()

    for k,v in stat.iteritems():
        print("Key:%s Value:%s\n" % (k,v))

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

