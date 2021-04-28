import pathlib

from celery import Celery
from celery_yaml.loader import YamlLoader


config = str(pathlib.Path(__file__).parent / "config.yaml")


def test_loader():
    app = Celery()
    conf = YamlLoader(app, config, configure_logging=False)
    conf = conf.read_configuration()
    assert conf == {
        "broker_url": "amqp://guest:guest@rabbitmq:5672/",
        "imports": ["helloworld.tasks"],
        "result_backend": "rpc://",
    }

    assert app.conf.broker_url == "amqp://guest:guest@rabbitmq:5672/"
    assert app.conf.result_backend == "rpc://"
