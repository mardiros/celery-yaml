import pkg_resources

from .loader import add_yaml_option
from .pyramid import includeme

__version__ = pkg_resources.get_distribution("celery-yaml").version

__all__ = [
    "add_yaml_option",
    "includeme",
]
