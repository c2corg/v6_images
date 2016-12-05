import os
import requests
from sqlalchemy import create_engine
from c2corg_images.scripts import MultithreadProcessor
from c2corg_images.resizing import create_resized_images, resized_keys
from c2corg_images.storage import S3Storage, temp_storage, active_storage

import logging
log = logging.getLogger(__name__)

V5_DATABASE_URL = os.environ.get('V5_DATABASE_URL', None)
BUCKET_DATABASE_URL = os.environ.get('BUCKET_DATABASE_URL', None)


class Migrator(MultithreadProcessor):

    def __init__(self, *args, **kwargs):
        super(MultithreadProcessor, self).__init__(*args, **kwargs)
        self._init_v5_database()
        self._init_bucket_database()

    def _init_v5_database(self):
        self.v5_engine = create_engine(V5_DATABASE_URL)
        self.v5_connection = self.v5_engine.connect()
        sql = """
CREATE TEMPORARY TABLE temp_images
(
  image_archive_id integer primary key,
  filename character varying(30) unique,
  has_svg boolean
);

INSERT INTO temp_images (
  image_archive_id,
  filename,
  has_svg
)
SELECT
  min(image_archive_id),
  filename,
  has_svg
FROM app_images_archives
GROUP BY filename, has_svg
ORDER BY min(image_archive_id);
"""
        self.v5_connection.execute(sql)

    def _init_bucket_database(self):
        self.bucket_engine = create_engine(BUCKET_DATABASE_URL)
        self.bucket_connection = self.bucket_engine.connect()
        sql = """
CREATE TABLE IF NOT EXISTS {} (
    key character varying(30) PRIMARY KEY
);
""".format(self._bucket_name())
        self.bucket_connection.execute(sql)

    def _bucket_name(self):
        if isinstance(active_storage, S3Storage):
            return active_storage._bucket_name
        else:
            return 'local_active_folder'

    def _is_marked_migrated(self, key):
        sql = """
SELECT count(*) AS count
FROM {}
WHERE key = '{}';
""".format(self._bucket_name(), key)
        if self.bucket_connection.execute(sql).fetchone()['count'] == 1:
            return True

    def _is_migrated(self, key):
        if self._is_marked_migrated(key):
            log.debug('{} is marked as migrated'.format(key))
            return True

        if active_storage.exists(key):
            log.debug('{} exists in active_storage'.format(key))
            self._set_migrated(key)
            return True

    def _set_migrated(self, key):
        if self._is_marked_migrated(key):
            return
        sql = """
INSERT INTO {} (key) VALUES ('{}');
        """.format(self._bucket_name(), key)
        self.bucket_connection.execute(sql)

    def do_keys(self):
        batch_size = 500
        offset = 0
        sql = """
SELECT count(*) AS count
FROM temp_images;
"""
        self.total = self.v5_connection.execute(sql).fetchone()['count']

        while offset < self.total:
            sql = """
SELECT
  filename,
  has_svg
FROM temp_images
ORDER BY image_archive_id {}
LIMIT {} OFFSET {};
""".format(os.environ.get('V5_ORDER', 'ASC'), batch_size, offset)
            result = self.v5_connection.execute(sql)
            for row in result:
                filename = row['filename']
                if row['has_svg'] is True:
                    base, ext = os.path.splitext(filename)
                    filename = '{}.svg'.format(base)
                yield filename

            offset += batch_size
        self.v5_connection.close()

    def do_process_key(self, key):
        base, ext = os.path.splitext(key)
        if ext == '.svg':
            for rasterized in ('{}.jpg'.format(base),
                               '{}.png'.format(base)):
                if active_storage.exists(rasterized):
                    log.info("{} delete file {}".format(key, rasterized))
                    active_storage.delete(rasterized)

        to_create = [key] + resized_keys(key)
        if not self.force:
            for key_to_create in list(to_create):
                if self._is_migrated(key_to_create):
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
                assert active_storage.exists(key_to_create)
                self._set_migrated(key_to_create)
            else:
                log.warning('{} File does not exists, skipping upload of {}'.
                            format(key, key_to_create))

        with self.lock:
            self.processed += 1
