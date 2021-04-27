"""Helper for celery."""

import logging
import os
from logging.config import dictConfig

import yaml
import celery.loaders.base
from celery import Celery

log = logging.getLogger(__name__)


class YamlLoader(celery.loaders.base.BaseLoader):
    """Celery loader based on yaml file."""

    def __init__(
        self, app: Celery, config: str, *, configure_logging: bool = True
    ) -> None:
        self.app = app
        self.config_path = config
        self.configure_logging = configure_logging
        super(YamlLoader, self).__init__(app)

    def read_configuration(self) -> dict:
        """Override this method to configure the celery app."""
        with open(self.config_path, "r") as stream:
            _conf = yaml.safe_load(stream)
            if "CELERY_BROKER_URL" in os.environ:
                # override the browker url
                _conf["celery"]["broker_url"] = os.environ["CELERY_BROKER_URL"]

            self.app.config_from_object(_conf["celery"])
            if self.configure_logging and "logging" in _conf:
                dictConfig(_conf["logging"])
        return _conf.get("app", {})
