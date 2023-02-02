import os
from typing import TYPE_CHECKING

import pkg_resources
from celery import Celery

if TYPE_CHECKING:
    from pyramid import Configurator  # type: ignore


def resolve_entrypoint(use: str) -> Celery:
    entrypoint = "celery_yaml.app"
    try:
        pkg, name = use.split("#")
    except ValueError:
        pkg, name = use, "main"
    try:
        scheme, pkg = pkg.split(":")
    except ValueError:
        scheme = "egg"
    if scheme != "egg":
        raise ValueError(f"{use}: unsupported scheme {scheme}")

    distribution = pkg_resources.get_distribution(pkg)
    runner = distribution.get_entry_info(entrypoint, name)
    app = runner.resolve() if runner else None
    if not isinstance(app, Celery):
        raise ValueError(f"{use} does not point to a valid Celery instance.")
    return app


def includeme(config: "Configurator") -> None:
    settings = config.registry.settings
    app = resolve_entrypoint(settings["celery"].pop("use"))
    celeryconf = settings["celery"]
    if "CELERY_BROKER_URL" in os.environ:
        # override the browker url
        celeryconf["broker_url"] = os.environ["CELERY_BROKER_URL"]
    app.config_from_object(celeryconf)
