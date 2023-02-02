import logging

from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.router import Router

from .tasks import add

log = logging.getLogger(__name__)


def add_service(request):
    val = request.GET.getall("val")
    if not val or len(val) != 2:
        return Response("Missing argument val. usage: /?val=1&val=2")
    log.info("Will delay the compute of the addition")
    async_result = add.delay(int(val[0]), int(val[1]))
    log.info("Waiting for the response")
    result = async_result.get()
    return Response(f"{val[0]} + {val[1]} = {result}")


def main(global_config: dict, **settings) -> Router:
    """Build the pyramid WSGI App."""

    with Configurator(settings=settings) as config:
        config.include("celery_yaml")
        config.add_route("root", "/")
        config.add_view(add_service, route_name="root")
        app = config.make_wsgi_app()
        return app
