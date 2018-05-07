import os
import shutil
import random
from datetime import datetime

from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden, HTTPBadRequest

from wand.image import Image

from c2cwsgiutils import stats

from c2corg_images.cropping import create_cropped_image
from c2corg_images.resizing import create_resized_images, resized_keys
from c2corg_images.storage import temp_storage, incoming_storage, active_storage

import logging
log = logging.getLogger(__name__)


@view_config(route_name='ping')
def ping(request):
    return Response('Pong!' % request.matchdict)


def get_format(path: str, filename: str) -> str:
    # imagemagick returns 'PNG' for SVG files
    base, ext = os.path.splitext(filename)
    if ext.upper() == '.SVG':
        return 'SVG'

    with stats.timer_context(['upload', 'get_format']):
        with Image(filename=path) as image:
            return image.format


epoch = datetime(1970, 1, 1)


def create_pseudo_unique_key() -> str:
    # https://github.com/c2corg/camptocamp.org/blob/1e60b94803765ca09fba533755dad0ecd4cad262/apps/frontend/lib/c2cTools.class.php  # noqa
    since_epoch = int((datetime.now() - epoch).total_seconds())
    return "%d_%d" % (since_epoch, random.randint(0, 2**31 - 1))


def crop_and_publish_thumbs(filename, crop_options):
    create_cropped_image(temp_storage.path(), filename, crop_options)
    create_resized_images(temp_storage.path(), filename)
    for key in resized_keys(filename):
        temp_storage.move(key, active_storage)


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
    pre_key = create_pseudo_unique_key()

    log.debug('%s - received upload request', pre_key)
    # Store the original image as raw file
    raw_file = '%s/%s_raw' % (temp_storage.path(), pre_key)
    with stats.timer_context(['upload', 'read']):
        input_file = request.POST['file'].file
        input_file.seek(0)
        with open(raw_file, 'wb') as output_file:
            shutil.copyfileobj(input_file, output_file)
            log.debug('%s - copied raw file to %s', pre_key, output_file)

    try:
        kind = get_format(raw_file, request.POST['file'].filename)
        log.debug('%s - detected format is %s', pre_key, kind)
    except Exception:
        raise HTTPBadRequest('Bad format for %s' % request.POST['file'].filename)

    if kind == 'JPEG':
        kind = 'jpg'
    elif kind in ('PNG', 'GIF', 'SVG'):
        kind = kind.lower()
    else:
        raise HTTPBadRequest('Unsupported image format %s' % kind)

    # Rename to official extension
    original_key = "{}.{}".format(pre_key, kind)
    os.rename(raw_file, temp_storage.object_path(original_key))

    create_resized_images(temp_storage.path(), original_key)

    log.debug('%s - uploading original file', pre_key)
    temp_storage.move(original_key, incoming_storage)

    for key in resized_keys(original_key):
        log.debug('%s - uploading resized image %s', pre_key, key)
        temp_storage.move(key, incoming_storage)

    log.debug('%s - returning response', pre_key)
    return {'filename': pre_key + '.' + kind}


@view_config(route_name='publish', renderer='json')
def publish(request):
    if request.POST['secret'] != os.environ['API_SECRET_KEY']:
        raise HTTPForbidden('Bad secret key')
    filename = request.POST['filename']
    already_published = active_storage.exists(filename)
    if 'crop' in request.POST:
        crop_options = request.POST['crop']
        if already_published:
            active_storage.copy(filename, temp_storage)
        else:
            incoming_storage.copy(filename, temp_storage)
        crop_and_publish_thumbs(filename, crop_options)
        temp_storage.delete(filename)
    else:
        for key in resized_keys(filename):
            if incoming_storage.exists(key):
                incoming_storage.move(key, active_storage)
    if not already_published:
        incoming_storage.move(filename, active_storage)
    return {'success': True}


@view_config(route_name='recrop', renderer='json')
def recrop(request):
    if request.POST['secret'] != os.environ['API_SECRET_KEY']:
        raise HTTPForbidden('Bad secret key')
    # Retrieve and rename file
    old_filename = request.POST['filename']
    base, ext = os.path.splitext(old_filename)
    active_storage.move(old_filename, temp_storage)
    filename = '{name}{ext}'.format(name=create_pseudo_unique_key(), ext=ext)
    os.rename(temp_storage.object_path(old_filename), temp_storage.object_path(filename))
    temp_storage.copy(filename, active_storage)
    # Crop and generate thumbnails
    if 'crop' in request.POST:
        crop_options = request.POST['crop']
        crop_and_publish_thumbs(filename, crop_options)
    else:
        create_resized_images(temp_storage.path(), filename)
        for key in resized_keys(filename):
            temp_storage.move(key, active_storage)
    temp_storage.delete(filename)
    return {'filename': filename}


@view_config(route_name='delete', renderer='json')
def delete(request):
    if request.POST['secret'] != os.environ['API_SECRET_KEY']:
        raise HTTPForbidden('Bad secret key')
    filenames = request.POST.getall('filenames')
    for filename in filenames:
        try:
            active_storage.delete(filename)
        except Exception:
            log.error('Deleting {} failed'.format(filename), exc_info=True)

        for key in resized_keys(filename):
            try:
                active_storage.delete(key)
            except Exception:
                log.error('Deleting {} failed'.format(key), exc_info=True)

    return {'success': True}
