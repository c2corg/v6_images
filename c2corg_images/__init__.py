from pyramid.config import Configurator
from pyramid.renderers import JSON
from pyramid.events import NewRequest
import os

# See http://docs.wand-py.org/en/0.4.1/guide/resizecrop.html
# Max 800, keep aspect ratio
# Max 120x120 don't keep ratio
THUMBNAIL_CONFIGS = [
    {'suffix': 'BI', 'geometry': '800x800>'},
    {'suffix': 'MI', 'geometry': '250x250>'},
    {'suffix': 'SI', 'geometry': '120x120!'}
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
