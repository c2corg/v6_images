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
        count_result = connection.execute(sql)
        for row in count_result:
            total = row['count']

        while offset < total:
            sql = """
SELECT filename
FROM app_images_archives
LIMIT {} OFFSET {};
""".format(batch_size, offset)

            result = connection.execute(sql)
            for row in result:
                yield row['filename']

            offset += batch_size
        connection.close()

    def do_process_key(self, key):
        if not self.force and active_storage.exists(key):
            with self.lock:
                self.skipped += 1
            return

        log.debug('{} getting file in temp storage'.format(key))
        r = requests.get('http://s.camptocamp.org/uploads/images/{}'.
                         format(key),
                         stream=True)
        with open(temp_storage.object_path(key), 'wb') as fd:
            for chunk in r.iter_content(None):
                fd.write(chunk)

        log.debug('{} creating resized images'.format(key))
        create_resized_images(temp_storage.path(), key)

        log.debug('{} uploading files to active storage'.format(key))
        temp_storage.move(key, active_storage)
        for resized in resized_keys(key):
            temp_storage.move(resized, active_storage)

        with self.lock:
            self.processed += 1
