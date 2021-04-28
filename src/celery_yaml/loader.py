"""Helper for celery."""
import logging
import os
import sys
from logging.config import dictConfig

import yaml
from celery import VERSION as celery_version
import celery.loaders.base
from celery import Celery

log = logging.getLogger(__name__)


if celery_version.major < 5:

    from celery.signals import user_preload_options

    @user_preload_options.connect
    def on_preload_parsed(options, **kwargs):
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


def add_yaml_option(app):

    help = "Celery configuration in a YAML file."
    if celery_version.major < 5:

        def add_preload_arguments(parser):
            parser.add_argument("--yaml", default=None, help=help)

        app.user_options["preload"].add(add_preload_arguments)

    else:

        from click import Option
        from celery import bootsteps

        app.user_options["preload"].add(Option(["--yaml"], required=True, help=help))

        class YamlBootstep(bootsteps.Step):
            def __init__(self, parent, yaml: str = "", **options):
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
        return _conf["celery"]
