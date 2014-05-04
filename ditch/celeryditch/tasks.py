from __future__ import absolute_import

import socket

import sys
from os.path import abspath
from unipath import Path

BASE_PATH = Path(abspath(__file__)).ancestor(1)
SCRIPT_PATH = BASE_PATH.ancestor(2).child('scripts')
print("BasePath:%s" % BASE_PATH)

sys.path.append(SCRIPT_PATH)
print("Appended script path:%s" % SCRIPT_PATH)

hn = socket.gethostname()

from .celery import app

@app.task(queue='ditch',name='mgr.tasks.status')
def status():
    print("Getting system status..")
    return {}


@app.task(queue='ditch',name='mgr.tasks.read_sensors')
def read_sensors():
    pass

@app.task(queue='ditch',name='mgr.tasks.pump_enable')
def pump_enable(bEnable):
    pass


@app.task(queue='ditch',name='mgr.tasks.south_enable')
def south_enable(bEnable):
    pass


@app.task(queue='ditch',name='mgr.tasks.north_enable')
def north_enable(bEnable):
    pass

