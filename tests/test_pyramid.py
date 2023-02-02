import pathlib

import yaml
from pyramid.config import Configurator  # type: ignore
from pyramid_helloworld.backend import app  # type: ignore

from celery_yaml import includeme
from celery_yaml.pyramid import resolve_entrypoint


def test_resolve_entrypoint():
    hello_app = resolve_entrypoint("egg:pyramid_helloworld")
    assert hello_app == app


def test_includeme():
    fpath = str(pathlib.Path(__file__).parent / "config.yaml")

    with open(fpath, "r") as stream:
        settings = yaml.safe_load(stream)

    config = Configurator(settings=settings['app'])
    includeme(config)
    assert app.conf.broker_url == "amqp://guest:guest@rabbitmq:5672/"
    assert app.conf.result_backend == "rpc://"
