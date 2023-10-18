"""Helper for celery."""
import logging
import os
import sys
from argparse import ArgumentParser
from logging.config import dictConfig
from typing import Any, Mapping

import celery.loaders.base
import yaml
from celery import VERSION as celery_version  # type: ignore
from celery import Celery

log = logging.getLogger(__name__)


if celery_version.major < 5:

    from celery.signals import user_preload_options  # type: ignore

    @user_preload_options.connect
    def on_preload_parsed(options: Mapping[str, Any], **kwargs: Any) -> None:
        config_path = options["yaml"]
        app = kwargs["app"]

        if config_path is None:
            print("You must provide the --yaml argument")
            sys.exit(-1)

        try:
            loader = YamlLoader(app, config=config_path)
            loader.read_configuration()
        except Exception as err:
            print(err)
            sys.exit(-1)


def add_yaml_option(app: Celery) -> None:

    help = "Celery configuration in a YAML file."
    if celery_version.major < 5:

        def add_preload_arguments(parser: ArgumentParser) -> None:
            parser.add_argument("--yaml", default=None, help=help)

        app.user_options["preload"].add(add_preload_arguments)

    else:

        from celery import bootsteps
        from click import Option

        app.user_options["preload"].add(Option(["--yaml"], required=True, help=help))

        class YamlBootstep(bootsteps.Step):
            def __init__(self, parent: Any, yaml: str = "", **options: Any) -> None:
                try:
                    loader = YamlLoader(app, config=yaml)
                    loader.read_configuration()
                    loader.import_default_modules()
                except Exception as err:
                    print(err)
                    sys.exit(-1)
                super().__init__(parent, **options)

        app.steps["worker"].add(YamlBootstep)


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

            # amqp is a cached_property that has to be refreshed
            del self.app.amqp

            if hasattr(self.app, "on_yaml_loaded"):
                getattr(self.app, "on_yaml_loaded")(_conf, config_path=self.config_path)
        return _conf["celery"]
