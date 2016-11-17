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
        self.connection = self.v5_engine.connect()
        sql = """
CREATE TEMPORARY TABLE temp_images
(
  image_archive_id integer primary key,
  filename character varying(30) unique
);

INSERT INTO temp_images (image_archive_id, filename)
SELECT min(image_archive_id), filename
  FROM app_images_archives
  GROUP BY filename
  ORDER BY min(image_archive_id);
"""
        self.connection.execute(sql)

    def do_keys(self):
        batch_size = 500
        offset = 0
        sql = """
SELECT count(*) AS count
FROM temp_images;
"""
        total = self.connection.execute(sql).fetchone()['count']

        while offset < total:
            sql = """
SELECT filename
FROM temp_images
ORDER BY image_archive_id {}
LIMIT {} OFFSET {};
""".format(os.environ.get('V5_ORDER', 'ASC'), batch_size, offset)
            result = self.connection.execute(sql)
            for row in result:
                yield row['filename']

            offset += batch_size
        self.connection.close()

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
                if r.status_code != 200:
                    log.error("{} return status code {} - {}".
                              format(key, r.status_code, r.reason))
                    with self.lock:
                        self.errors += 1
                    return
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
        for key_to_create in to_create:
            if temp_storage.exists(key_to_create):
                log.debug('{} uploading {}'.format(key, key_to_create))
                temp_storage.move(key_to_create, active_storage)
            else:
                log.warning('{} File does not exists, skipping upload of {}'.
                            format(key, key_to_create))

        with self.lock:
            self.processed += 1
