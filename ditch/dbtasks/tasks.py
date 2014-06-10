from __future__ import absolute_import

import json
import time

from celery import shared_task

@shared_task()
def onstatus(d):
    """
    Handle the status results
    """

    status = json.loads(d)

    for k,v in status.iteritems():
        print("Key:%s Value:%s\n" % (k,v))

    print("Status:%s" % status)
    secs = time.mktime(time.localtime())
    print "asctime(localtime(secs)): %s" % time.asctime(time.localtime(secs))

