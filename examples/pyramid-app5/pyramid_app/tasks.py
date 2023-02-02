import logging

from .backend import app

log = logging.getLogger(__name__)


@app.task(name="add")
def add(val0, val1):
    log.info(f"Adding values {val0} and {val1}")
    return val0 + val1
