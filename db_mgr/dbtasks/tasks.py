from __future__ import absolute_import

import celery
import json
import time

@celery.task()
def onstatus(d):
    """
    Handle the status results
    """

    status = d

    for k,v in status.iteritems():
        print("Key:%s Value:%s\n" % (k,v))

    print("Status:%s" % status)
    secs = time.mktime(time.localtime())
    print "asctime(localtime(secs)): %s" % time.asctime(time.localtime(secs))

