from __future__ import absolute_import

from .celery import app
from json import loads

@app.task
def onstatus(d):
    """
    Handle the status results
    """

    status = loads(d)

    for k,v in status.iteritems():
        print("Key:%s Value:%s\n" % (k,v))

    print("Status:%s" % status)

