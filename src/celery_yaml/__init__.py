import importlib.metadata

from .loader import add_yaml_option
from .pyramid import includeme

__version__ = importlib.metadata.version("plaster-yaml")

__all__ = [
    "add_yaml_option",
    "includeme",
]
