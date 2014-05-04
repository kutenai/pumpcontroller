from __future__ import absolute_import

from celery import Celery

app = Celery('gbmgr',include=['gbmgr.tasks'])
app.config_from_object('gbmgr.celeryconfig')

