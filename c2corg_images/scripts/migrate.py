from c2corg_images.scripts import MultithreadProcessor
from c2corg_images.resizing import original_pattern, create_resized_images, resized_keys
from c2corg_images.storage import v5_storage, temp_storage, active_storage
import requests

import logging
log = logging.getLogger(__name__)


class Migrator(MultithreadProcessor):

    def do_keys(self):
        for key in v5_storage.keys():
            match = original_pattern.match(key)
            if match:
                yield key

    def do_process_key(self, key):
        if not self.force and active_storage.exists(key):
            with self.lock:
                self.skipped += 1
            return

        log.debug('{} getting file in temp storage'.format(key))
        import os
        if os.environ['STORAGE_BACKEND'] == 's3':
            r = requests.get('http://s.camptocamp.org/uploads/images/{}'.
                             format(key),
                             stream=True)
            with open(temp_storage.object_path(key), 'wb') as fd:
                for chunk in r.iter_content(None):
                    fd.write(chunk)
        else:
            v5_storage.copy(key, temp_storage)

        log.debug('{} creating resized images'.format(key))
        create_resized_images(temp_storage.path(), key)

        log.debug('{} uploading files to active storage'.format(key))
        temp_storage.move(key, active_storage)
        for resized in resized_keys(key):
            temp_storage.move(resized, active_storage)

        with self.lock:
            self.processed += 1
