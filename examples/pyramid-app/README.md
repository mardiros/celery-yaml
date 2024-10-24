# Pyramid and Celery using Yaml Configuration Demo

This pyramid app use Celery 5 as a backend to compute addition.

## Configuration

Pyramid and Celery configuration are unified in a `development.yaml`
file.

The `.env` file contains the `broker_url` to avoid password to be stored
in the configuration file. In real life, this file stay uncommited.

This file is read by `docker-compose` and inject in the `celery_backend`
container, see `docker-compose.yaml` file.

## Running

#### Start the service

```sh
alias dc=docker-compose
dc up -d rabbitmq && sleep 2 && dc up -d celery_backend && sleep 2 && dc up -d pyramid_app && dc logs -f
```

The backend must be started before the app, some strange behavior I honnestly
don't understand.

### Testing

```sh
curl "http://localhost:8000?val=17&val=25"
17 + 25 = 42
```