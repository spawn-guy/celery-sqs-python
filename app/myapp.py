from celery import Celery
import time

from celery.app.task import BaseTask
from kombu.asynchronous.http.curl import CurlClient

from app.base_task import AppBaseTask
from app.config import CELERY_BROKER, REDIS_HOST, REDIS_PORT, REDIS_DATABASE, CELERY_SQS_URL

app = Celery(
    "myapp",
    broker=CELERY_BROKER,
    broker_pool_limit=10,
    result_backend=f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DATABASE}",
    redis_backend_health_check_interval=30,
    result_backend_thread_safe=True,
    # Redis is thead-safe
    result_backend_max_connections=100,
    # The maximum number of connections that can be open in the connection pool.
    result_expires=60 * 60,  # 60 minutes
    # Time (in seconds, or a timedelta object) for when after stored task tombstones will be deleted.
    result_extended=True,
    # Enables extended task result attributes
    # (name, args, kwargs, worker, retries, queue, delivery_info)
    # to be written to backend.
    result_compression="zlib",
    task_acks_late=True,
    worker_prefetch_multiplier=16,
    task_default_queue="default_static",
    task_queues={
        "default_static": {
            "exchange": "default_static",
            "routing_key": "default_static",
        }
    },
    broker_transport_options={
        # # !!!! same as in AWS-SQS: Visibility timeout. match the time of the longest ETA you’re planning to use.
        # # chatGPT: Set the SQS visibility timeout on the queue to be slightly longer than the longest running task.
        # "visibility_timeout": 1200,  # seconds.
        "visibility_timeout": 20,  # seconds.
        # # Celery: seconds to sleep between unsuccessful polls
        # "polling_interval": 1,  # seconds.
        # # !!!! same as in AWS-SQS: Receive message wait time
        # "wait_time_seconds": 20,  # seconds.
        "region": "eu-west-1",
        "predefined_queues": {
            "default_static": {
                "url": CELERY_SQS_URL,
            }
        }
    }
)


@app.task
def is_pycurl_available():
    try:
        import pycurl
    except ImportError:  # pragma: no cover
        print('pycurl is not installed')
    else:
        print('pycurl is installed')
        print(f"PycURL version: {pycurl.version}")
        print(f"PycURL version info: {pycurl.version_info()}")

    if CurlClient.Curl is not None:
        print('CurlClient.Curl is not None')
    else:
        print('CurlClient.Curl is None')

    return "ok"


@app.task
def add(x, y):
    time.sleep(0.05)  # Simulate 50ms task execution time
    return x + y


# @app.task(bind=True, autoretry_for=(Exception,), retry_backoff=5, max_retries=5)
@app.task(bind=True, autoretry_for=(Exception,), max_retries=3)  # default retry_backoff=180s
def bad_throw(self: BaseTask, x, y):
    # time.sleep(0.05)  # Simulate 50ms task execution time
    print('Try {0}/{1}'.format(self.request.retries, self.max_retries))
    if self.request.retries == 0:
        raise Exception("bad_throw 0")  # countdown=retry_backoff
    if self.request.retries == 1:
        # return self.retry(exc=Exception("bad_throw.retry 1"))  # default countdown=180s
        return self.retry(exc=Exception("bad_throw.retry 1"), countdown=3)  # countdown=3s
    return x + y


@app.task(base=AppBaseTask, bind=True)
def bad_throw_base(self: AppBaseTask, x, y):
    # time.sleep(0.05)  # Simulate 50ms task execution time
    print('Try {0}/{1}'.format(self.request.retries, self.max_retries))
    if self.request.retries == 0:
        raise Exception("bad_throw_base 0")  # countdown=retry_backoff
    if self.request.retries == 1:
        # return self.retry(exc=Exception("bad_throw_base.retry 1"))  # default countdown=180s
        return self.retry(exc=Exception("bad_throw_base.retry 1"), countdown=7)  # countdown=7s
    return x + y


if __name__ == "__main__":
    # celery -A myapp worker -l INFO -P gevent
    app.start()
