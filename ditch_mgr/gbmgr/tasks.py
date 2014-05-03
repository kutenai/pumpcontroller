from __future__ import absolute_import

from gbmgr.celery import app

@app.task
def onstatus(d):
    """
    Handle the status results
    """

    for k,v in d.iteritems():
        print("Key:%s Value:%s\n" % (k,v))

    print("Status:%s" % d)

