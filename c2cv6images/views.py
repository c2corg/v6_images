import os
import uuid
import shutil
from pyramid.response import Response
from pyramid.view import view_config

from c2cv6images.convert import create_thumbnail

INCOMING = "incoming"


@view_config(route_name='hello')
def hello_world(request):
    return Response('Hello %(name)s!' % request.matchdict)


@view_config(route_name='upload', renderer='json')
def upload(request):
    input_file = request.POST['file'].file
    filename = "%s.jpg" % uuid.uuid4()
    file_path = os.path.join(INCOMING, filename)

    # Store the original image
    input_file.seek(0)
    with open(file_path, 'wb') as output_file:
        shutil.copyfileobj(input_file, output_file)

    # Create an optimized thumbnail
    create_thumbnail(INCOMING, filename)

    return {'filename': filename}
