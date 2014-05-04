from __future__ import absolute_import

import socket

import sys
from os.path import abspath
from unipath import Path

from celery import shared_task


@shared_task(queue='ditch',name='mgr.tasks.status')
def status():
    print("Getting system status..")
    return {}


@shared_task(queue='ditch',name='mgr.tasks.read_sensors')
def read_sensors():
    pass

@shared_task(queue='ditch',name='mgr.tasks.pump_enable')
def pump_enable(bEnable):
    pass


@shared_task(queue='ditch',name='mgr.tasks.south_enable')
def south_enable(bEnable):
    pass


@shared_task(queue='ditch',name='mgr.tasks.north_enable')
def north_enable(bEnable):
    pass

