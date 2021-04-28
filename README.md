# Easy Configuration For Celery App Using a Yaml File

`celery-yaml` is a library to inject a --yaml option to the `celery worker`
command in order to inject its configuration.

It also handle help to configurate this application for Pyramid application.

## Usage

### With Celery 4

```sh
celery worker -A my_application.module_containing_my.app --yaml development.yaml ...
```

### With Celery 5

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
  broker_url: 'amqp://guest:guest@localhost:5672//'
  result_backend: 'rpc://'
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

The broker_url can also be override by an environment variable `CELERY_BROKER_URL`
to avoid password in the configuration file.
---

## Using Celery in a Pyramid App.

The extras "pyramid" must be added to install the extras depencencies.

### With poetry

```toml
[tool.poetry.dependencies]
celery-yaml = { version = "^0.1.3", extras = ["pyramid"] }
```

Then some entry_points have to configure, such as:

```toml
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
  result_backend: 'rpc://'
  imports:
      - pyramid_app.tasks

app:
  "use": "egg:pyramid_app"
  "pyramid.includes": ["celery_yaml"]
  "celery":
    <<: *celery
    "use": "egg:pyramid_app"

```

#### See full example in the examples directory:

##### Pyramid with Celery 4
https://github.com/mardiros/celery-yaml/tree/master/examples/pyramid-app

##### Pyramid with Celery 5

https://github.com/mardiros/celery-yaml/tree/master/examples/pyramid-app5
