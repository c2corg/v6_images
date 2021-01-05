import c2cwsgiutils.pyramid  # type: ignore
from c2cwsgiutils.health_check import HealthCheck  # type: ignore
from pyramid.config import Configurator  # type: ignore
from pyramid.events import NewRequest  # type: ignore
import os
import json


def parse_resizing_config(serialized_config):
    if serialized_config is not None:
        return json.loads(serialized_config)
    else:
        # See documentation at http://www.imagemagick.org/Usage/resize
        return [
            {'suffix': 'BI', 'convert': ['-resize', '1500x1500>', '-quality', '90']},
            {'suffix': 'MI', 'convert': ['-resize', '400x400>', '-quality', '90']},
            {'suffix': 'SI', 'convert': ['-resize', '200x200^', '-gravity', 'center',
                                         '-extent', '200x200', '-quality', '90']}
        ]


RESIZING_CONFIG = parse_resizing_config(os.environ.get('RESIZING_CONFIG', None))


def add_cors_headers_response_callback(event):
    def cors_headers(request, response):
        response.headers.update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST,GET,OPTIONS',
            'Access-Control-Allow-Headers': 'Origin, Content-Type, Accept, Authorization',
            'Access-Control-Max-Age': '1728000',
        })
    event.request.add_response_callback(cors_headers)


def main(_, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings, route_prefix=os.environ.get('ROUTE_PREFIX', '/'))
    config.include(c2cwsgiutils.pyramid.includeme)
    config.add_route('ping', '/ping')
    config.add_route('upload', '/upload')
    config.add_route('publish', '/publish')
    config.add_route('recrop', '/recrop')
    config.add_route('delete', '/delete')
    config.add_static_view(name='active', path=os.environ['ACTIVE_FOLDER'])
    config.add_subscriber(add_cors_headers_response_callback, NewRequest)

    HealthCheck(config)

    config.scan("c2corg_images")

    return config.make_wsgi_app()
