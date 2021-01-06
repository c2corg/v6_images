import os
import re
from typing import Dict
from c2corg_images import RESIZING_CONFIG
from c2corg_images.convert import transform, rasterize_svg
from c2cwsgiutils import stats

import logging
log = logging.getLogger(__name__)

original_pattern = re.compile(r'(\d+_\d+)\.(\w+)')


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


def _get_size(config):
    try:
        convert = config['convert']
        resize_pos = convert.index('-resize')
        return convert[resize_pos + 1]
    except Exception:
        return 'unknown'


def create_resized_image(path: str, original: str, config: Dict) -> str:
    original_path = os.path.join(path, original)
    resized = resized_key(original, config)
    resized_path = os.path.join(path, resized)
    resize_config = config['convert']
    log.info('Creating resized image %s with options %s', resized_path, resize_config)
    with stats.timer_context(['transform', 'resize', _get_size(config)]):
        transform(original_path,
                  resized_path,
                  resize_config)
    return resized


def create_resized_images(path, key):
    base, ext = os.path.splitext(key)
    raster_file = False
    if ext == '.svg':
        svg_key = key
        jpg_key = '{}{}'.format(base, '.jpg')
        with stats.timer_context(['transform', 'rasterize_svg']):
            rasterize_svg(os.path.join(path, svg_key), os.path.join(path, jpg_key))
        raster_file = os.path.join(path, jpg_key)
        key = jpg_key

    for config in RESIZING_CONFIG:
        create_resized_image(path, key, config)

    if raster_file:
        os.unlink(raster_file)
