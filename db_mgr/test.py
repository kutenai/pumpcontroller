#!/usr/bin/env python

import json
from celery import Celery

app = Celery()
app.config_from_object('celeryconfig')

from dbtasks.tasks import onstatus

if __name__ == "__main__":

    s = '{"Sump": "653", "P": "0", "NC": "0", "STen": "0", "N": "0", "PC": "0", "S": "0", "ST": "0", "SC": "0", "Ditch": "765"}'
    j = json.loads(s)

    print("Name:%s" % onstatus.name)

    onstatus.delay(j)



