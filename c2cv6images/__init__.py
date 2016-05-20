from pyramid.config import Configurator
from pyramid.renderers import JSON


config = Configurator()
config.add_renderer('myjson', JSON())

config.add_route('hello', '/hello/{name}')
config.add_route('upload', '/upload')

config.scan()

app = config.make_wsgi_app()
