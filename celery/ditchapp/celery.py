from __future__ import absolute_import
from celery import Celery

print("Initialize the Celery App.")

app = Celery(include=[
    'ditchtasks.tasks',
    'dbtasks.tasks'])
app.config_from_object('celeryconfig')
