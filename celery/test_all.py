#!/usr/bin/env python

from dbtasks.tasks import onstatus
from ditchtasks.tasks import status

if __name__ == "__main__":

    print("Name:%s" % status.name)

    result = status.delay()

    print("Result:%s" % result)

    s = result.get(timeout=1)
    print("Status:%s" % s)

    onstatus.delay(s)

