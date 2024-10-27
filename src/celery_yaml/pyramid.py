import os
from typing import TYPE_CHECKING, Any

from celery import Celery

try:
    from plaster_yaml.loader import resolve_use
except ImportError:

    def resolve_use(use: str, entrypoint: str) -> Any:
        raise LookupError("Install celery_yaml[pyramid]")


if TYPE_CHECKING:
    from pyramid import Configurator  # type: ignore


def resolve_entrypoint(use: str) -> Celery:
    entrypoint = "celery_yaml.app"
    app = resolve_use(use, entrypoint)
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
