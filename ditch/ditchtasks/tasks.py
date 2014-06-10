from __future__ import absolute_import

from celery import shared_task

@shared_task()
def status():
    print("Getting system status..")
    return {}


@shared_task()
def read_sensors():
    pass

@shared_task()
def pump_enable(bEnable):
    pass


@shared_task()
def south_enable(bEnable):
    pass


@shared_task()
def north_enable(bEnable):
    pass

