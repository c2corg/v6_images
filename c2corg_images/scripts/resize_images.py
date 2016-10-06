import sys
import argparse

from c2corg_images.resizing import original_pattern, create_resized_images, resized_keys
from c2corg_images.storage import temp_storage, active_storage

import logging
log = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)


def main(argv=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-v', '--verbose', dest='verbose',
        action='store_const', const=True, default=False,
        help='Increase verbosity')
    args = vars(parser.parse_args(argv[1:]))

    if args['verbose']:
        log.setLevel(logging.DEBUG)

    resize_images()


def resize_images():
    for key in active_storage.keys():
        match = original_pattern.match(key)
        if match:

            log.debug('{} getting file in temp storage'.format(key))
            active_storage.copy(key, temp_storage)

            log.debug('{} creating resized images'.format(key))
            create_resized_images(temp_storage.path(), key)

            log.debug('{} uploading files to active storage'.format(key))
            for resized in resized_keys(key):
                temp_storage.move(resized, active_storage)

            temp_storage.delete(key)
