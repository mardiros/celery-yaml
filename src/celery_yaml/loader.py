"""Helper for celery."""

import logging
import os
import sys
from logging.config import dictConfig
from typing import Any, Mapping

from click import Option
import celery.loaders.base
import yaml
from celery import Celery
from celery.signals import user_preload_options  # type: ignore

log = logging.getLogger(__name__)


@user_preload_options.connect
def on_preload_parsed(options: Mapping[str, Any], **kwargs: Any) -> None:
    config_path = options["yaml"]
    app = kwargs["app"]

    if config_path is None:
        print("You must provide the --yaml argument")
        sys.exit(-1)

    loader = YamlLoader(app, config=config_path)
    loader.read_configuration()


def add_yaml_option(app: Celery) -> None:
    help = "Celery configuration in a YAML file."
    app.user_options["preload"].add(Option(["--yaml"], required=True, help=help))


class YamlLoader(celery.loaders.base.BaseLoader):
    """Celery loader based on yaml file."""

    def __init__(
        self, app: Celery, config: str, *, configure_logging: bool = True
    ) -> None:
        self.app = app
        self.config_path = config
        self.configure_logging = configure_logging
        super(YamlLoader, self).__init__(app)

    def read_configuration(
        self, env: str = "CELERY_CONFIG_MODULE"
    ) -> Mapping[str, Any]:
        """Override this method to configure the celery app."""
        with open(self.config_path, "r") as stream:
            _conf = yaml.safe_load(stream)
            if "CELERY_BROKER_URL" in os.environ:
                # override the browker url
                _conf["celery"]["broker_url"] = os.environ["CELERY_BROKER_URL"]

            self.app.config_from_object(_conf["celery"])
            if self.configure_logging and "logging" in _conf:
                dictConfig(_conf["logging"])

            if hasattr(self.app, "on_yaml_loaded"):
                getattr(self.app, "on_yaml_loaded")(_conf, config_path=self.config_path)
        return _conf["celery"]
