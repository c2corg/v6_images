from pyramid.config import Configurator
from pyramid.renderers import JSON
from pyramid.events import NewRequest
import os

RESIZING_CONFIG = [
    {'suffix': 'BI', 'convert': ['-resize', '800x800>']},
    {'suffix': 'MI', 'convert': ['-resize', '250x250>']},
    {'suffix': 'SI', 'convert': ['-resize', '150x150^',
                                 '-gravity', 'center',
                                 '-extent', '150x150']}
]


def add_cors_headers_response_callback(event):
    def cors_headers(request, response):
        response.headers.update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST,GET,OPTIONS',
            'Access-Control-Allow-Headers': 'Origin, Content-Type, Accept, Authorization',
            'Access-Control-Max-Age': '1728000',
        })
    event.request.add_response_callback(cors_headers)

config = Configurator()
config.add_renderer('myjson', JSON())

config.add_route('ping', '/ping')
config.add_route('upload', '/upload')
config.add_route('publish', '/publish')
config.add_static_view(name='active', path=os.environ['ACTIVE_FOLDER'])
config.add_subscriber(add_cors_headers_response_callback, NewRequest)

config.scan()

app = config.make_wsgi_app()
