from __future__ import absolute_import

import json
from celery import shared_task

@shared_task(queue = 'gb',name='gbmgr.tasks.onstatus')
def onstatus(st):
    """
    Handle the status results
    """
    print("On Status Called..")

    st = json.loads(st)

    from .models import LevelLog

    ll = LevelLog.objects.create(
        ditchlvl    = st.get('Ditch'),
        sumplvl     = st.get('Sump'),
        ditch_inches= 0,
        sump_inches = 0,
        pump_on     = st.get('P') == '1',
        north_on    = st.get('N') == '1',
        south_on    = st.get('S') == '1'
    )

    ll.save()

    print("Inserted new status entry.")

    return "Success"

