import os
import shutil
import random
from datetime import datetime

from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden

from wand.image import Image

from c2corg_images import THUMBNAIL_CONFIGS
from c2corg_images.convert import (
    create_thumbnail,
    rasterize_svg,
    format_config_template)
from c2corg_images.storage import temp_storage, incoming_storage, active_storage

import logging
log = logging.getLogger(__name__)


@view_config(route_name='ping')
def ping(request):
    return Response('Pong!' % request.matchdict)


def get_format(filename: str) -> str:
    with Image(filename=filename) as image:
        return image.format


epoch = datetime(1970, 1, 1)


def create_pseudo_unique_key() -> str:
    # https://github.com/c2corg/camptocamp.org/blob/1e60b94803765ca09fba533755dad0ecd4cad262/apps/frontend/lib/c2cTools.class.php  # noqa
    since_epoch = int((datetime.now() - epoch).total_seconds())
    return "%d_%d" % (since_epoch, random.randint(0, 2**31 - 1))


@view_config(route_name='upload', request_method='OPTIONS')
def upload_options(request):
    request.response.headers.update({
        'Access-Control-Allow-Origin': request.headers['Origin'],
        'Access-Control-Allow-Methods': 'POST,GET,OPTIONS',
        'Access-Control-Allow-Headers': 'Origin, Content-Type, Accept, Authorization',
        'Access-Control-Max-Age': '1728000',
    })
    return request.response


@view_config(route_name='upload', renderer='json')
def upload(request):
    input_file = request.POST['file'].file
    pre_key = create_pseudo_unique_key()

    log.debug('%s - received upload request', pre_key)
    # Store the original image as raw file
    raw_file = '%s/%s_raw' % (temp_storage.path(), pre_key)
    input_file.seek(0)
    with open(raw_file, 'wb') as output_file:
        shutil.copyfileobj(input_file, output_file)
        log.debug('%s - copied raw file to %s', pre_key, output_file)

    try:
        kind = get_format(raw_file)
        log.debug('%s - detected format is %s', pre_key, kind)
    except:
        log.exception('Bad format for %s', output_file)
        return {'error': 'Unknown image format'}

    if kind == 'JPEG':
        kind = 'jpg'
    elif kind == 'PNG' or kind == 'GIF':
        kind = kind.lower()
    elif kind == 'SVG':
        # Save the original SVG file and
        # FIXME: why do we need to rasterize?
        # Quality: we should rasterize directly from SVG to thumbnails
        original_svg_file = temp_storage.object_path("%s.svg".format(pre_key))
        os.rename(raw_file, original_svg_file)
        log.debug('%s - rasterizing SVG', pre_key)
        rasterize_svg(original_svg_file, raw_file)
        log.debug('%s - rasterizing SVG - done', pre_key)
        kind = 'png'
    else:
        request.response.status_code = 400
        return {'error': 'Unsupported image format %s' % kind}

    # Rename to official extension
    original_key = "{}.{}".format(pre_key, kind)
    os.rename(raw_file, temp_storage.object_path(original_key))

    # Create an optimized thumbnail
    for config in THUMBNAIL_CONFIGS:
        log.debug('%s - creating thumbnail %s', pre_key, config['template'])
        thumbnail = create_thumbnail(temp_storage.path(), pre_key, kind, config)
        log.debug('%s - creating thumbnail done %s', pre_key, config['template'])
        thumbnail_key = os.path.basename(thumbnail)

        log.debug('%s - uploading thumbnail %s', pre_key, config['template'])
        temp_storage.move(thumbnail_key, incoming_storage)
        log.debug('%s - uploading thumbnail done %s', pre_key, config['template'])

    log.debug('%s - uploading original file', pre_key)
    temp_storage.move(original_key, incoming_storage)
    log.debug('%s - uploading original file done', pre_key)

    log.debug('%s - returning response', pre_key)
    return {'filename': pre_key + '.' + kind}


def _keys_to_publish(key):
    keys = [key]
    for config in THUMBNAIL_CONFIGS:
        base, ext = os.path.splitext(key)
        keys.append(format_config_template('', base, ext[1:], config['template']).strip('/'))
    return keys


@view_config(route_name='publish', renderer='json')
def publish(request):
    if request.POST['secret'] != os.environ['API_SECRET_KEY']:
        raise HTTPForbidden('Bad secret key')
    filename = request.POST['filename']
    for key in _keys_to_publish(filename):
        incoming_storage.move(key, active_storage)
    return {'success': True}
