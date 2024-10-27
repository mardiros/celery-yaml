import pathlib

import pytest
import yaml
from pyramid.config import Configurator  # type: ignore
from pyramid_helloworld.backend import app  # type: ignore

from celery_yaml import includeme
from celery_yaml.pyramid import resolve_entrypoint


def test_resolve_entrypoint():
    hello_app = resolve_entrypoint("egg:pyramid_helloworld")
    assert hello_app == app


def test_resolve_entrypoint_missing():
    with pytest.raises(ValueError) as cxt:
        resolve_entrypoint("egg:plaster_yaml")
    assert (
        str(cxt.value) == "Entrypoint celery_yaml.app is missing for egg:plaster_yaml"
    )


def test_resolve_entrypoint_lookuperror():
    with pytest.raises(ValueError) as cxt:
        resolve_entrypoint("egg:app1#app_ko")
    assert (
        str(cxt.value) == "egg:app1#app_ko does not point to a valid Celery instance."
    )


def test_includeme():
    fpath = str(pathlib.Path(__file__).parent / "config.yaml")

    with open(fpath) as stream:
        settings = yaml.safe_load(stream)

    config = Configurator(settings=settings["app"])
    includeme(config)
    assert app.conf.broker_url == "amqp://guest:guest@rabbitmq:5672/"
    assert app.conf.result_backend == "rpc://"
