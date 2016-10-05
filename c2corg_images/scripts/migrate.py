import sys
import argparse

from c2corg_images.thumbnails import original_pattern, create_thumbnails, thumbnail_keys
from c2corg_images.storage import v5_storage, temp_storage, active_storage

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

    migrate()


def migrate():
    count = 0
    for key in v5_storage.keys():
        match = original_pattern.match(key)
        if match:
            if active_storage.exists(key):
                continue

            log.debug('{} getting file in temp storage'.format(key))
            v5_storage.copy(key, temp_storage)

            log.debug('{} creating thumbnails'.format(key))
            create_thumbnails(temp_storage.path(), key)

            log.debug('{} uploading files to active storage'.format(key))
            temp_storage.move(key, active_storage)
            for thumbnail in thumbnail_keys(key):
                temp_storage.move(thumbnail, active_storage)
            count += 1
    return count
