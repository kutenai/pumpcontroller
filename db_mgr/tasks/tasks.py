from __future__ import absolute_import

def onstatus(d,queue='db'):
    """
    Insert status results into the GardenBuzz database.
    """

    status = loads(d)

    for k,v in status.iteritems():
        print("Key:%s Value:%s\n" % (k,v))

    print("Status:%s" % status)
    secs = time.mktime(time.localtime())
    print "asctime(localtime(secs)): %s" % time.asctime(time.localtime(secs))

