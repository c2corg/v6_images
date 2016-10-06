import os
import re
from typing import Dict
from c2corg_images import RESIZING_CONFIG
from c2corg_images.convert import transform, rasterize_svg

import logging
log = logging.getLogger(__name__)

original_pattern = re.compile('(\d+_\d+)\.(\w+)')

resized_patterns = []
for config in RESIZING_CONFIG:
    pattern = '(\d+_\d+){}\.(\w+)'.format(config['suffix'])
    resized_patterns.append(re.compile(pattern))


def resized_key(original, config):
    base, ext = os.path.splitext(original)
    if ext == '.svg':
        ext = '.jpg'
    return "{}{}{}".format(base, config['suffix'], ext)


def resized_keys(original):
    keys = []
    for config in RESIZING_CONFIG:
        keys.append(resized_key(original, config))
    return keys


def create_resized_image(path: str, original: str, config: Dict) -> str:
    original_path = os.path.join(path, original)
    resized = resized_key(original, config)
    resized_path = os.path.join(path, resized)
    log.info('Creating resized image %s', resized_path)
    transform(original_path,
              resized_path,
              config['convert'])
    return resized


def create_resized_images(path, key):
    base, ext = os.path.splitext(key)
    raster_file = False
    if ext == '.svg':
        svg_key = key
        jpg_key = '{}{}'.format(base, '.jpg')
        rasterize_svg(os.path.join(path, svg_key), os.path.join(path, jpg_key))
        raster_file = os.path.join(path, jpg_key)
        key = jpg_key

    for config in RESIZING_CONFIG:
        create_resized_image(path, key, config)

    if raster_file:
        os.unlink(raster_file)
