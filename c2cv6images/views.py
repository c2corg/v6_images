import os
import shutil
import random
from datetime import datetime

from pyramid.response import Response
from pyramid.view import view_config

from wand.image import Image

from c2cv6images.convert import create_thumbnail, rasterize_svg

INCOMING = "incoming"


@view_config(route_name='hello')
def hello_world(request):
    return Response('Hello %(name)s!' % request.matchdict)


def get_format(filename):
    with Image(filename=filename) as image:
        return image.format


epoch = datetime(1970, 1, 1)


def create_pseudo_unique_key():
    # https://github.com/c2corg/camptocamp.org/blob/1e60b94803765ca09fba533755dad0ecd4cad262/apps/frontend/lib/c2cTools.class.php  # noqa
    since_epoch = int((datetime.now() - epoch).total_seconds())
    return "%d_%d" % (since_epoch, random.randint(0, 2**31 - 1))


@view_config(route_name='upload', renderer='json')
def upload(request):
    input_file = request.POST['file'].file
    pre_key = create_pseudo_unique_key()

    # Store the original image as raw file
    raw_file = '%s/%s_raw' % (INCOMING, pre_key)
    input_file.seek(0)
    with open(raw_file, 'wb') as output_file:
        shutil.copyfileobj(input_file, output_file)

    kind = get_format(raw_file)
    if kind == 'JPEG':
        kind = 'jpg'
    elif kind == 'PNG' or kind == 'GIF':
        kind = kind.lower()
    elif kind == 'SVG':
        # Save the original SVG file and
        # FIXME: why do we need to rasterize?
        # Quality: we should rasterize directly from SVG to thumbnails
        original_svg_file = "%s/%s.svg" % (INCOMING, pre_key)
        os.rename(raw_file, original_svg_file)
        rasterize_svg(original_svg_file, raw_file)
        kind = 'png'
    else:
        request.response.status_code = 400
        return {'error': 'Unsupported image format %s' % kind}

    # Rename to official extension
    original_file = "%s/%s.%s" % (INCOMING, pre_key, kind)
    os.rename(raw_file, original_file)

    # Create an optimized thumbnail
    filename = create_thumbnail(INCOMING, pre_key, kind)

    return {'filename': filename}
