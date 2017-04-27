import os
from c2corg_images.convert import transform

import logging
log = logging.getLogger(__name__)


def create_cropped_image(path: str, filename: str, crop_options: str):
    full_path = os.path.join(path, filename)
    log.info('Cropping image %s', full_path)
    crop_config = ['-crop', crop_options, '+repage']
    transform(full_path,
              full_path,
              crop_config)
