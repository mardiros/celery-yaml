import pathlib

from celery import Celery

from celery_yaml.loader import YamlLoader

config = str(pathlib.Path(__file__).parent / "config.yaml")
config_no_broker = str(pathlib.Path(__file__).parent / "config-no-broker.yaml")


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


def test_loader_celery_broker_in_environ(monkeypatch):
    monkeypatch.setenv("CELERY_BROKER_URL", "amqp://guest:guest@rabbitmqenv:5672/")
    app = Celery()
    conf = YamlLoader(app, config_no_broker, configure_logging=False)
    conf = conf.read_configuration()
    assert conf == {
        "broker_url": "amqp://guest:guest@rabbitmqenv:5672/",
        "imports": ["helloworld.tasks"],
        "result_backend": "rpc://",
    }

    assert app.conf.broker_url == "amqp://guest:guest@rabbitmqenv:5672/"
    assert app.conf.result_backend == "rpc://"
