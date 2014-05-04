from celery import group,chain
import time
from datetime import datetime
import json

from optparse import make_option
from django.core.management.base import BaseCommand

from celeryditch.tasks import status
from celeryapp.tasks import onstatus

from ditchmon.models import LevelLog

class Command(BaseCommand):
    args = ''
    help = '''
    Write a status value to the level log.
    '''

    option_list = BaseCommand.option_list + (
        make_option('--dummy',
                    dest='dummy',
                    default=None,
                    help='This is how I\'d specify an option if I wanted to.'),
    )

    def handle(self, *args, **options):
        """Generates sidebar sprite for schemeit only.
        TODO: Generate sprite for partsim.
        """

        dummy_opt = options.get('dummy',None)

        s = status.apply_async()

        st = json.loads(s.get())

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
