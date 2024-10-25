import pathlib
from collections.abc import Mapping
from typing import Any

from celery import Celery

from celery_yaml.loader import YamlLoader, add_yaml_option

config = str(pathlib.Path(__file__).parent / "config.yaml")
config_no_broker = str(pathlib.Path(__file__).parent / "config-no-broker.yaml")
config_envsub = str(pathlib.Path(__file__).parent / "config-envsub.yaml")


class CeleryApp(Celery):
    database_dsn: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_yaml_option(self)

    def on_yaml_loaded(self, config: Mapping[str, Any], config_path: str) -> None:
        self.database_dsn = config["app"]["database_dsn"]


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


def test_loader_celery_broker_subenv(monkeypatch):
    monkeypatch.setenv("DATABASE_DSN", "postgresql://scott:tiger@db/zoo")
    app = CeleryApp()
    conf = YamlLoader(app, config_envsub, configure_logging=False)
    conf = conf.read_configuration()
    assert conf == {
        "broker_url": "amqp://guest:guest@rabbitmq:5672/",
        "imports": ["helloworld.tasks"],
        "result_backend": "redis://redis/0",
    }

    assert app.conf.broker_url == "amqp://guest:guest@rabbitmq:5672/"
    assert app.conf.result_backend == "redis://redis/0"

    assert app.database_dsn == "postgresql://scott:tiger@db/zoo"


def test_loader_celery_from_other_key(monkeypatch):
    monkeypatch.setenv("DATABASE_DSN", "postgresql://scott:tiger@db/zoo")
    app = Celery()
    conf = YamlLoader(app, config, config_key="celery2", configure_logging=False)
    conf.read_configuration()
    assert app.conf.broker_url == "amqp://guest:guest@rabbitmq:5672/other"
