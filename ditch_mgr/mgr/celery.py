from __future__ import absolute_import

from celery import Celery

app = Celery('mgr',
             broker='redis://gardenbuzz.com:6379/0',
             backend='redis://gardenbuzz.com:6379/1',
             include=['mgr.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
    )

if __name__ == '__main__':
    app.start()

