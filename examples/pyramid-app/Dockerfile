FROM python:3.8-slim
LABEL maintainer="guillaume@gauvr.it"

WORKDIR /srv/pyramid_app
EXPOSE 8000

RUN pip install poetry

RUN useradd pyramid_app --home /home/pyramid_app && \
    mkdir -p /home/pyramid_app && \
    chown -R pyramid_app:pyramid_app /home/pyramid_app && \
    chown -R pyramid_app:pyramid_app /srv/pyramid_app
USER pyramid_app

COPY pyproject.toml poetry.lock /srv/pyramid_app/
RUN poetry install --no-dev
COPY . /srv/pyramid_app/
RUN poetry install --no-dev

CMD ["poetry", "run", "pserve", "development.yaml"]
