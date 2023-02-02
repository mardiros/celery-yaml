import logging

from celery import Celery
from celery.signals import task_failure

from celery_yaml import add_yaml_option

app = Celery()
add_yaml_option(app)

log = logging.getLogger(__name__)


@task_failure.connect
def log_errors(sender, exception, traceback, args, kwargs, **_kwargs):
    """Log traceback when an exception occuded while processing a task."""
    log.error(
        "Exception occured while running task %s(*%r, **%r)",
        sender.name,
        args,
        kwargs,
        exc_info=(exception.__class__, exception, traceback),
    )
