import pathlib
from collections.abc import Mapping
from typing import Any

import pytest
from celery import Celery
from celery.schedules import crontab

from celery_yaml.loader import YamlLoader, add_yaml_option, build_crontab

config = str(pathlib.Path(__file__).parent / "config.yaml")
config_no_broker = str(pathlib.Path(__file__).parent / "config-no-broker.yaml")
config_envsub = str(pathlib.Path(__file__).parent / "config-envsub.yaml")
config_beat = str(pathlib.Path(__file__).parent / "config-celerybeat.yaml")


class CeleryApp(Celery):
    database_dsn: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_yaml_option(self)

    def on_yaml_loaded(self, config: Mapping[str, Any], config_path: str) -> None:
        self.database_dsn = config["app"]["database_dsn"]


@pytest.mark.parametrize(
    "params,expected",
    [
        pytest.param(
            {"key": {"task": "dummy", "schedule": 10}},
            {"key": {"task": "dummy", "schedule": 10}},
            id="every 10s",
        ),
        pytest.param(
            {"key": {"task": "dummy", "schedule": {"hour": "0", "minute": "0"}}},
            {"key": {"task": "dummy", "schedule": crontab(hour="0", minute="0")}},
            id="crontab",
        ),
        pytest.param(
            {
                "key": {
                    "task": "dummy",
                    "schedule": {"hour": "9", "minute": "0", "day_of_week": "2"},
                }
            },
            {
                "key": {
                    "task": "dummy",
                    "schedule": crontab(hour="9", minute="0", day_of_week="2"),
                }
            },
            id="crontab dow",
        ),
    ],
)
def test_crontab(params: Mapping[str, Any], expected: Mapping[str, Any]):
    assert dict(build_crontab(params)) == expected


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


def test_beat_loader():
    app = Celery()
    conf = YamlLoader(app, config_beat, configure_logging=False)
    conf = conf.read_configuration()
    assert conf == {
        "beat_schedule": {
            "beat_it": {
                "schedule": crontab(hour="9", minute="0", day_of_week="1"),
                "task": "beat_it",
            },
        },
        "broker_url": "amqp://guest:guest@rabbitmq:5672/",
        "imports": [
            "helloworld.tasks",
        ],
    }
    assert app.conf.beat_schedule == {
        "beat_it": {
            "schedule": crontab(hour="9", minute="0", day_of_week="1"),
            "task": "beat_it",
        },
    }


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
