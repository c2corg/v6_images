import os
import re
from typing import Dict
from c2corg_images import THUMBNAIL_CONFIGS
from c2corg_images.convert import transform, optimize

import logging
log = logging.getLogger(__name__)

original_pattern = re.compile('(\d+_\d+)\.(\w+)')

thumbnail_patterns = []
for config in THUMBNAIL_CONFIGS:
    pattern = '(\d+_\d+){}\.(\w+)'.format(config['suffix'])
    thumbnail_patterns.append(re.compile(pattern))


def thumbnail_key(original, config):
    base, ext = os.path.splitext(original)
    return "{}{}{}".format(base, config['suffix'], ext)


def thumbnail_keys(original):
    keys = []
    for config in THUMBNAIL_CONFIGS:
        keys.append(thumbnail_key(original, config))
    return keys


def original_key(thumbnail):
    for pattern in thumbnail_patterns:
        match = pattern.match(thumbnail)
        if match:
            return "{}.{}".format(match.groups)


def create_thumbnail(path: str, key: str, config: Dict[str, str]) -> str:
    original_path = os.path.join(path, key)
    tkey = thumbnail_key(key, config)
    thumbnail_path = os.path.join(path, tkey)
    log.info('Creating thumbnail %s', path)
    transform(original_path,
              thumbnail_path,
              config['geometry'])
    optimize(thumbnail_path)
    return tkey
