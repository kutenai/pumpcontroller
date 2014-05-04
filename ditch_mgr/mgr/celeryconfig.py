BROKER_URL = 'redis://gardenbuzz.com:6379/0'
CELERY_RESULT_BACKEND = 'redis://gardenbuzz.com:6379/1'

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT=['json']
CELERY_TIMEZONE = 'US/Mountain'
CELERY_ENABLE_UTC = True
CELERYD_CONCURRENCY = 1
CELERY_TASK_RESULT_EXPIRES=3600

