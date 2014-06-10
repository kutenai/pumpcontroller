#!/usr/bin/env python

from celery import chain

from dbtasks.tasks import onstatus
from ditchtasks.tasks import status

if __name__ == "__main__":

    print("Name:%s" % status.name)
    print("OnStatus:%s" % onstatus.name)

    ch = chain(status.s() | onstatus.s())

    result = ch.apply_async()

    result = status.delay()

    print("Result:%s" % result)

