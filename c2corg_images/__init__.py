from pyramid.config import Configurator
from pyramid.renderers import JSON


config = Configurator()
config.add_renderer('myjson', JSON())

config.add_route('ping', '/ping')
config.add_route('upload', '/upload')
config.add_static_view(name='active', path='/root/active')

config.scan()

app = config.make_wsgi_app()
