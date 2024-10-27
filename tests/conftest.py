import sys
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def root() -> Path:
    return Path(__file__).parent.absolute()


@pytest.fixture(scope="session", autouse=True)
def fake_packages(root: Path) -> None:
    fake_packages = root / "dummy_packages"
    for dirs in fake_packages.iterdir():
        sys.path.insert(0, str(dirs))
