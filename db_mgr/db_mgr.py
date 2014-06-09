#!/usr/bin/env python
from __future__ import absolute_import

import time
from json import loads
from celery import Celery

app = Celery('mgr')
app.config_from_object('celeryconfig')

# Optional configuration, see the application user guide.
app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
    )

@app.task(queue='db')
def onstatus(d):
    """
    Insert status results into the GardenBuzz database.
    """

    status = loads(d)

    for k,v in status.iteritems():
        print("Key:%s Value:%s\n" % (k,v))

    print("Status:%s" % status)
    secs = time.mktime(time.localtime())
    print "asctime(localtime(secs)): %s" % time.asctime(time.localtime(secs))



if __name__ == '__main__':
    app.start()

