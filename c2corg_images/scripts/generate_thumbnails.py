import sys
import argparse

from c2corg_images.thumbnails import original_pattern, create_thumbnails, thumbnail_keys
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

    generate_thumbnails()


def generate_thumbnails():
    for key in active_storage.keys():
        match = original_pattern.match(key)
        if match:

            log.debug('{} getting file in temp storage'.format(key))
            active_storage.copy(key, temp_storage)

            log.debug('{} creating thumbnails'.format(key))
            create_thumbnails(temp_storage.path(), key)

            log.debug('{} uploading files to active storage'.format(key))
            for thumbnail in thumbnail_keys(key):
                temp_storage.move(thumbnail, active_storage)

            temp_storage.delete(key)
