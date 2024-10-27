package := 'celery_yaml'
default_test_suite := 'tests'

install:
    uv sync --group dev

lint:
    uv run ruff check .

test: lint mypy unittest

unittest test_suite=default_test_suite:
    uv run pytest -sxv {{test_suite}}

lf:
    uv run pytest -sxvvv --lf

cov test_suite=default_test_suite:
    rm -f .coverage
    rm -rf htmlcov
    uv run pytest --cov-report=html --cov={{package}} {{test_suite}}
    xdg-open htmlcov/index.html

mypy:
    uv run mypy src/ tests/

fmt:
    uv run ruff check --fix .
    uv run ruff format src tests

release major_minor_patch: test && changelog
    # uvx pdm self add pdm-bump
    uvx pdm bump {{major_minor_patch}}
    uv sync

changelog:
    uv run python scripts/write_changelog.py
    cat CHANGELOG.md >> CHANGELOG.md.new
    rm CHANGELOG.md
    mv CHANGELOG.md.new CHANGELOG.md
    $EDITOR CHANGELOG.md

publish:
    git commit -am "Release $(uv run scripts/get_version.py)"
    git push
    git tag "v$(uv run scripts/get_version.py)"
    git push origin "v$(uv run scripts/get_version.py)"
