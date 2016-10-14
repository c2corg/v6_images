from c2corg_images.scripts import MultithreadProcessor
from c2corg_images.resizing import original_pattern, create_resized_images, resized_keys
from c2corg_images.storage import temp_storage, active_storage

import logging
log = logging.getLogger(__name__)


class Resizer(MultithreadProcessor):

    def do_keys(self):
        for key in active_storage.keys():
            match = original_pattern.match(key)
            if match:
                yield key

    def do_process_key(self, key):
        log.debug('{} getting file in temp storage'.format(key))
        active_storage.copy(key, temp_storage)

        log.debug('{} creating resized images'.format(key))
        create_resized_images(temp_storage.path(), key)

        log.debug('{} uploading files to active storage'.format(key))
        for resized in resized_keys(key):
            temp_storage.move(resized, active_storage)

        temp_storage.delete(key)

        with self.lock:
            self.processed += 1
