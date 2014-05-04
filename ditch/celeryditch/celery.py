from __future__ import absolute_import

from celery import Celery

print("Initialize mgr Celery app.")

app = Celery('mgr',include=['celeryditch.tasks'])
app.config_from_object('celeryditch.celeryconfig')

