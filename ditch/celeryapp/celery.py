from __future__ import absolute_import

from celery import Celery

print("Initialize gbmgr Celery app.")

app = Celery('gbmgr')
app.config_from_object('celeryapp.celeryconfig')


