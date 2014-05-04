from celery import group,chain
import time
from datetime import datetime
import json

from optparse import make_option
from django.core.management.base import BaseCommand

from celeryditch.tasks import status
from ditchmon.tasks import onstatus

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

        import djcelery
        djcelery.setup_loader()

        dummy_opt = options.get('dummy',None)

        res = (status.s() | onstatus.s()).apply_async()
        print("Result:%s" % res.get())
