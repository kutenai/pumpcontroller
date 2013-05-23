import os
import sys

path = '/Users/kutenai/proj/bondiproj/pumpcontrol/webapp/ditch'
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE','ditch.settings.dev')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
