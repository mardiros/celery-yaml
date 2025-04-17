[![Continuous Integration](https://github.com/mardiros/celery-yaml/actions/workflows/tests.yml/badge.svg)](https://github.com/mardiros/celery-yaml/actions/workflows/tests.yml)
[![Coverage Report](https://codecov.io/gh/mardiros/celery-yaml/branch/master/graph/badge.svg)](https://codecov.io/gh/mardiros/celery-yaml)

# Easy Configuration For Celery App Using a Yaml File

`celery-yaml` is a library to inject a --yaml option to the `celery worker`
command in order to inject its configuration.

It also handle help to configurate this application for Pyramid application.

## Usage

```sh
celery -A my_application.module_containing_my.app worker --yaml development.yaml ...
```

This will configure the application `my_application` containing an application
`app` in a submodule `module_containing_my`.

The celery app must register the `--yaml` using the `add_yaml_option` on the
app instance, this way:

```python
from celery import Celery
from celery_yaml import add_yaml_option

app = Celery()
add_yaml_option(app)
```

### Yaml format

```yaml
celery:
  broker_url: "amqp://guest:guest@localhost:5672//"
  result_backend: "rpc://"
  imports:
    - my_application.tasks
  # see all settings in the celery docs:
  # https://docs.celeryproject.org/en/stable/userguide/configuration.html

logging:
  version: 1
  # dictConfig format
  # https://docs.python.org/3/library/logging.config.html#logging-config-dictschema
```

---

**NOTE**

To **avoid password in** the **configuration file**:

- Every variables can be substitute with an environment variable.
  The yaml file will replace variable using [envsub](https://mardiros.github.io/envsub/).

  ```yaml
  celery:
    broker_url: "${CELERY_BROKER_URL-amqp://guest:guest@localhost:5672//}"

  ```

- **DEPRECATED**: The `broker_url` is always overriden by the environment variable
  `CELERY_BROKER_URL` without any declaration.

---

### Using celery beat

Celery beat can schedule tasks using interval or crontab.

The schedule parameter can be an int, a float or a mapping.
If it is a mapping, it will be cast to a [crontab](https://docs.celeryq.dev/en/stable/reference/celery.schedules.html#celery.schedules.crontab),
the mapping will be passed as acrontab parameters.

```yaml
celery:
  beat_schedule:
    beat_second:
      task: beat_it
      schedule: 10 # example of interval schedule, every 10 seconds

    beat_crontab:
      task: beat_it
      schedule: # example of crontab
        hour: 9
        minute: 0
        day_of_week: 1
```

## Using Celery in a Pyramid App.

The extras "pyramid" must be added to install the extras depencencies.

### With PEP 621 (uv, pdm, ...)

```toml
[dependency-groups]
celery = ["celery >=5.2.7,<6", "celery-yaml[pyramid]>=2.0.0,<3"]

[project.entry-points."paste.app_factory"]
main = "pyramid_helloworld:main"

[project.entry-points."celery_yaml.app"]
main = "pyramid_helloworld.backend:app"
```

### With poetry

```toml
[tool.poetry.dependencies]
celery-yaml = { version = "^2.0.0", extras = ["pyramid"] }

[tool.poetry.plugins."paste.app_factory"]
main = "pyramid_app.wsgi:main"

[tool.poetry.plugins."celery_yaml.app"]
main = "pyramid_app.backend:app"

[tool.poetry.plugins."plaster.loader_factory"]
"file+yaml" = "plaster_yaml:Loader"
```

the `paste.app_factory` is used by `Pyramid` itself to build the WSGI
sergivice but we add a `plaster.loader_factory` to configure the usage
of a yaml file instead of an `ini` file to configure it.

Then the `celery_yaml.app` is used by `celery-yaml` as an entrypoint to
the celery app.

Then, in the configuration file,

```yaml
celery: &celery
  result_backend: "rpc://"
  imports:
    - pyramid_app.tasks

app:
  "use": "egg:pyramid_app"
  "pyramid.includes": ["celery_yaml"]
  "celery":
    <<: *celery
    "use": "egg:pyramid_app"

foo: "bar"
```

### More configuration

if the celery app as a method `on_yaml_loaded` then the function
is called with the data and the filepath in parameter.
It may be used to get mode configuration available readed from the yaml file.

#### Example

```python
from celery import Celery as CeleryBase


class Celery(CeleryBase):

    def on_yaml_loaded(self, data: dict[str, Any], config_path: str):
        data['foo']  # you can access to the value of foo here

```

This is particullary usefull for depenency injection purpose.

#### Environment substitution

```yaml
celery:
  broker_url: ${CELERY_BROKER_URL}
  result_backend: ${CELERY_BACKEND_RESULT}
  imports:
    - pyramid_app.tasks

database_dsn: ${DATABASE_DSN}
```

The `CELERY_BROKER_URL` and `CELERY_BACKEND_RESULT` environment variable
are interpreted by celery, so can be outside your yaml file, but, it is not
True for all the variable, using celery-yaml, you can still inject configuration
in the yaml that are substituted in the configuration during the yaml load.

This is particullary usefull to keep your configuration structured but keep
secrets in environment variable, for security reason. And also to build docker
container that can be easily customizable.

#### See full example in the examples directory:

https://github.com/mardiros/celery-yaml/tree/master/examples/pyramid-app
