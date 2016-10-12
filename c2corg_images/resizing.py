import os
import re
from typing import Dict
from c2corg_images import RESIZING_CONFIG
from c2corg_images.convert import transform

import logging
log = logging.getLogger(__name__)

original_pattern = re.compile('(\d+_\d+)\.(\w+)')

resized_patterns = []
for config in RESIZING_CONFIG:
    pattern = '(\d+_\d+){}\.(\w+)'.format(config['suffix'])
    resized_patterns.append(re.compile(pattern))


def resized_key(original, config):
    base, ext = os.path.splitext(original)
    return "{}{}{}".format(base, config['suffix'], ext)


def resized_keys(original):
    keys = []
    for config in RESIZING_CONFIG:
        keys.append(resized_key(original, config))
    return keys


def original_key(resized):
    for pattern in resized_patterns:
        match = pattern.match(resized)
        if match:
            return "{}.{}".format(match.groups)


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
    for config in RESIZING_CONFIG:
        create_resized_image(path, key, config)
