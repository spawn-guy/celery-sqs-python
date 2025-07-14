from typing import Optional

import kombu.transport.SQS
from celery import Task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


class AppBaseTask(Task):
    """
    autoretry_for
        A list/tuple of exception classes.
        If any of these exceptions are raised during the execution of the task, the task will automatically be retried.
    default: no exceptions will be auto-retried
        see: https://docs.celeryq.dev/en/stable/userguide/tasks.html#automatic-retry-for-known-exceptions
    """

    autoretry_for = (Exception,)

    """
    max_retries
        A number. Maximum number of retries before giving up.
        A value of None means task will retry forever.
    default: 3
    """
    max_retries = 5

    """
    retry_backoff
        A boolean.
        If this option is set to True, auto-retries will be delayed following the rules of exponential backoff.
        The first retry will have a delay of 1 second, the second retry will have a delay of 2 seconds,
        the third will delay 4 seconds, the fourth will delay 8 seconds, and so on.
        (However, this delay value is modified by retry_jitter, if it is enabled.)

        A number.
        If this option is set to a number, it is used as a delay factor.
        For example, if this option is set to 3, the first retry will delay 3 seconds, the second will delay 6 seconds,
        the third will delay 12 seconds, the fourth will delay 24 seconds, and so on.

     default: False, and auto-retries will not be delayed. but actually 180 seconds
    """
    retry_backoff = 3

    """
    retry_backoff_max
        A number. If retry_backoff is enabled, this option will set a maximum delay in seconds between task auto-retries.
    default: 600 (10 minutes).
    """
    retry_backoff_max = 600

    """
    retry_jitter
        A boolean. Jitter is used to introduce randomness into exponential backoff delays,
        to prevent all tasks in the queue from being executed simultaneously.
        If this option is set to True,
        the delay value calculated by retry_backoff is treated as a maximum,
        and the actual delay value will be a random number between zero and that maximum.
    default: True
    """
    retry_jitter = False

    def get_sqs_queue_url_by_task(self, task_name: str) -> Optional[str]:
        task_queue = self.app.amqp.router.route(options={}, name=task_name)["queue"]
        _url = None
        with self.app.producer_or_acquire(None) as P:
            if isinstance(P.channel, kombu.transport.SQS.Channel):
                _url = P.channel._resolve_queue_url(task_queue.name)
        return _url

    async def get_queue_size_by_task(self, task_name: str) -> Optional[int]:
        # via celery
        task_queue = self.app.amqp.router.route(options={}, name=task_name)["queue"]
        with self.app.producer_or_acquire(None) as P:
            # implemented in AbstractChannel
            size = P.channel._size(task_queue.name)

        return size
