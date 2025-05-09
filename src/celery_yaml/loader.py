"""Helper for celery."""

import logging
import os
import sys
from collections.abc import Iterator, Mapping
from logging.config import dictConfig
from typing import Any, Tuple

import celery.loaders.base
import envsub
import yaml
from celery import Celery
from celery.schedules import crontab
from celery.signals import user_preload_options  # type: ignore
from click import Option

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


def build_crontab(beat_schedule: Mapping[str, Any]) -> Iterator[Tuple[str, Any]]:
    for key, val in beat_schedule.items():
        if isinstance(val["schedule"], dict):
            val["schedule"] = crontab(**val["schedule"])
        yield key, val


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
        super().__init__(app)

    def read_configuration(
        self, env: str = "CELERY_CONFIG_MODULE"
    ) -> Mapping[str, Any]:
        """Override this method to configure the celery app."""
        with open(self.config_path) as downstream:
            with envsub.sub(downstream) as upstream:
                _conf = yaml.safe_load(upstream)
        _celery_config = _conf[self.config_key]

        if "CELERY_BROKER_URL" in os.environ:
            # override the browker url
            _celery_config["broker_url"] = os.environ["CELERY_BROKER_URL"]

        if "beat_schedule" in _celery_config:
            _celery_config["beat_schedule"] = dict(
                build_crontab(_celery_config["beat_schedule"])
            )

        self.app.config_from_object(_celery_config)
        if self.configure_logging and "logging" in _conf:
            dictConfig(_conf["logging"])
        if hasattr(self.app, "on_yaml_loaded"):
            self.app.on_yaml_loaded(_conf, config_path=self.config_path)
        return _celery_config
