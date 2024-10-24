"""Helper for celery."""

import logging
import os
import sys
from logging.config import dictConfig
from typing import Any, Mapping

from click import Option
import celery.loaders.base
import envsub
import yaml
from celery import Celery
from celery.signals import user_preload_options  # type: ignore

log = logging.getLogger(__name__)


@user_preload_options.connect
def on_preload_parsed(options: Mapping[str, Any], **kwargs: Any) -> None:
    config_path = options["yaml"]
    config_key = options["yaml_key"]
    app = kwargs["app"]

    if config_path is None:
        print("You must provide the --yaml argument")
        sys.exit(-1)

    loader = YamlLoader(app, config=config_path, config_key=config_key)
    loader.read_configuration()


def add_yaml_option(app: Celery) -> None:
    help = "Celery configuration in a YAML file."
    help_key = "The key that contains the celery configuration."
    app.user_options["preload"].add(Option(["--yaml"], required=True, help=help))
    app.user_options["preload"].add(
        Option(
            ["--yaml-key"],
            required=False,
            default="celery",
            show_default=True,
            help=help_key,
        )
    )


class YamlLoader(celery.loaders.base.BaseLoader):
    """Celery loader based on yaml file."""

    def __init__(
        self,
        app: Celery,
        config: str,
        *,
        config_key: str = "celery",
        configure_logging: bool = True,
    ) -> None:
        self.app = app
        self.config_path = config
        self.config_key = config_key
        self.configure_logging = configure_logging
        super(YamlLoader, self).__init__(app)

    def read_configuration(
        self, env: str = "CELERY_CONFIG_MODULE"
    ) -> Mapping[str, Any]:
        """Override this method to configure the celery app."""
        with open(self.config_path, "r") as downstream:
            with envsub.sub(downstream) as upstream:
                _conf = yaml.safe_load(upstream)
        _celery_config = _conf[self.config_key]
        if "CELERY_BROKER_URL" in os.environ:
            # override the browker url
            _celery_config["broker_url"] = os.environ["CELERY_BROKER_URL"]

        self.app.config_from_object(_celery_config)
        if self.configure_logging and "logging" in _conf:
            dictConfig(_conf["logging"])

        if hasattr(self.app, "on_yaml_loaded"):
            getattr(self.app, "on_yaml_loaded")(_conf, config_path=self.config_path)
        return _celery_config
