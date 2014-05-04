from __future__ import absolute_import

from celery import Celery

app = Celery('mgr',include=['mgr.tasks'])
app.config_from_object('mgr.celeryconfig')
