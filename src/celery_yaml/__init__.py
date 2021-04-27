import pkg_resources

from .loader import YamlLoader
from .pyramid import includeme

__version__ = pkg_resources.get_distribution("pyramid-helloworld").version
