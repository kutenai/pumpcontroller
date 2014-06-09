#!/usr/bin/env python

from celery import Celery

app = Celery()
app.config_from_object('celeryconfig')

from ditchtasks.tasks import status

if __name__ == "__main__":

    print("Name:%s" % status.name)

    result = status.delay()

    print("Result:%s" % result)

    s = result.get(timeout=1)
    print("Status:%s" % s)
