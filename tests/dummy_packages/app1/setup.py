from setuptools import find_packages, setup

setup(
    name="app1",
    version="1.0",
    packages=find_packages(),
    entry_points={
        "celery_yaml.app": [
            "app_ko=app1:app_ko",
            "app_ok=app1:app_ok",
        ],
    },
)
