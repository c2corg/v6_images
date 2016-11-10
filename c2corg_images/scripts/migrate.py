import os
import requests
from sqlalchemy import create_engine
from c2corg_images.scripts import MultithreadProcessor
from c2corg_images.resizing import create_resized_images, resized_keys
from c2corg_images.storage import temp_storage, active_storage

import logging
log = logging.getLogger(__name__)

V5_DATABASE_URL = os.environ.get('V5_DATABASE_URL', None)


class Migrator(MultithreadProcessor):

    def __init__(self, *args, **kwargs):
        super(MultithreadProcessor, self).__init__(*args, **kwargs)
        self.v5_engine = create_engine(V5_DATABASE_URL)

    def do_keys(self):
        batch_size = 500
        offset = 0
        connection = self.v5_engine.connect()
        sql = """
SELECT count(*) AS count
FROM app_images_archives;
"""
        total = connection.execute(sql).fetchone()['count']

        while offset < total:
            sql = """
SELECT filename
FROM app_images_archives
ORDER BY id {}
LIMIT {} OFFSET {};
""".format(os.environ.get('V5_ORDER', 'ASC'), batch_size, offset)
            result = connection.execute(sql)
            for row in result:
                yield row['filename']

            offset += batch_size
        connection.close()

    def do_process_key(self, key):
        to_create = [key] + resized_keys(key)
        if not self.force:
            for key_to_create in list(to_create):
                if active_storage.exists(key_to_create):
                    to_create.remove(key_to_create)
            if len(to_create) == 0:
                log.debug('{} skipping'.format(key))
                with self.lock:
                    self.skipped += 1
                    return

        log.debug('{} getting file in temp storage'.format(key))
        tries = 3
        success = False
        while tries > 0 and not success:
            try:
                r = requests.get('http://s.camptocamp.org/uploads/images/{}'.
                                 format(key),
                                 stream=True,
                                 timeout=120)
                with open(temp_storage.object_path(key), 'wb') as fd:
                    for chunk in r.iter_content(None):
                        fd.write(chunk)
                success = True
            except Exception as e:
                tries -= 1
                if tries > 0:
                    log.warning("{} retry download".format(key))
                else:
                    raise e

        log.debug('{} creating resized images'.format(key))
        create_resized_images(temp_storage.path(), key)

        log.debug('{} uploading files to active storage'.format(key))
        if key in to_create:
            log.debug('{} uploading {}'.format(key, key))
            temp_storage.move(key, active_storage)
        for resized in resized_keys(key):
            if resized in to_create:
                log.debug('{} uploading {}'.format(key, resized))
                temp_storage.move(resized, active_storage)

        with self.lock:
            self.processed += 1
