import os
from c2corg_images.convert import transform
from c2cwsgiutils import stats

import logging
log = logging.getLogger(__name__)


def create_cropped_image(path: str, filename: str, crop_options: str):
    full_path = os.path.join(path, filename)
    crop_config = ['-crop', crop_options, '+repage']
    log.info('Cropping image %s with options %s', full_path, crop_config)
    with stats.timer_context(['transform', 'crop']):
        transform(full_path,
                  full_path,
                  crop_config)
