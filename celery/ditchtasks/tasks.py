from __future__ import absolute_import

import sys
from unipath import Path
import json

BASE_PATH = Path(__file__).ancestor(2)
SCRIPT_PATH = BASE_PATH.ancestor(1).child('scripts')
print("BasePath:%s" % BASE_PATH)

sys.path.append(SCRIPT_PATH)
print("Appended script path:%s" % SCRIPT_PATH)

from ditchapp.celery import app

from Ditch.IrrigationAPIAT import IrrigationAPI

api = IrrigationAPI()

@app.task()
def status():
    print("Getting system status..")
    stat = api.getSystemStatus()

    #for k,v in stat.iteritems():
    #    print("Key:%s Value:%s\n" % (k,v))

    return json.dumps(stat)


@app.task()
def read_sensors():
    d = api.getSensorData()
    return json.dumps(d)


@app.task()
def pump_enable(bEnable):
    api.pumpEnable(bEnable)


@app.task()
def south_enable(bEnable):
    api.southEnable(bEnable)


@app.task()
def north_enable(bEnable):
    api.northEnable(bEnable)

