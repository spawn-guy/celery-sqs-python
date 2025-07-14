import os

from dotenv import dotenv_values

config = {
    **dotenv_values("../.env"),  # load shared development variables
    **dotenv_values("./.env"),  # load shared development variables
    **os.environ,  # override loaded values with environment variables
}

# celery
CELERY_BROKER = config.get('CELERY_BROKER')
CELERY_SQS_REGION = config.get('CELERY_SQS_REGION')
CELERY_SQS_URL = config.get('CELERY_SQS_URL')

# redis
REDIS_HOST = config.get('REDIS_HOST')
REDIS_PORT = int(config.get('REDIS_PORT'))
REDIS_DATABASE = int(config.get('REDIS_DATABASE'))
