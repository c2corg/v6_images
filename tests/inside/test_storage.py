import os
import unittest
import requests
from c2corg_images.storage import (
    S3Storage, LocalStorage, temp_storage, getS3Params)

from tests import utils, data_folder

import logging
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('s3transfer').setLevel(logging.CRITICAL)

key = 'test.png'
source_file = os.path.join(data_folder, 'images', 'piano.png')


class BaseStorageTest(unittest.TestCase):

    def standard_protocol(self):
        # put file in temp storage for processing
        temp_storage.put(key, source_file)

        # move it in incoming storage waiting for publication
        temp_storage.move(key, self.incoming_storage)
        assert self.incoming_storage.exists(key)
        assert not temp_storage.exists(key)

        # Ensure the file is private
        if isinstance(self.incoming_storage, S3Storage):
            url = '{}/{}/{}'.format(self.incoming_storage._endpoint_url,
                                    self.incoming_storage._bucket_name,
                                    key)
            r = requests.get(url, stream=True, timeout=120)
            assert r.status_code == 403

        # on publishing it is moved to active storage
        self.incoming_storage.move(key, self.active_storage)
        assert self.active_storage.exists(key)
        assert not self.incoming_storage.exists(key)

        # Ensure the file is public
        if isinstance(self.active_storage, S3Storage):
            url = '{}/{}/{}'.format(self.active_storage._endpoint_url,
                                    self.active_storage._bucket_name,
                                    key)
            r = requests.get(url, stream=True, timeout=120)
            assert r.status_code == 200
            assert r.headers['content-type'] == 'image/png'

        # cleaning
        self.active_storage.delete(key)
        assert not self.active_storage.exists(key)

        # delete file that does not exists
        self.active_storage.delete('test_not_exists.jpg')

    def resizing_protocol(self):
        # for resizing object is in active storage
        self.active_storage.put(key, source_file)

        # get object in temp storage
        self.active_storage.copy(key, temp_storage)
        assert temp_storage.exists(key)

        # resizing ...

        # moved it back to active storage
        temp_storage.move(key, self.active_storage)
        assert self.active_storage.exists(key)
        assert not temp_storage.exists(key)

        # cleaning
        self.active_storage.delete(key)
        assert not self.active_storage.exists(key)


class S3StorageTest(BaseStorageTest):

    def setUp(self):  # NOQA
        self.incoming_storage = S3Storage(os.environ['INCOMING_BUCKET'],
                                          getS3Params('INCOMING'),
                                          default_acl='private')
        self.active_storage = S3Storage(os.environ['ACTIVE_BUCKET'],
                                        getS3Params('ACTIVE'),
                                        default_acl='public-read')

    @utils.skipIfTravis
    def test_standard_protocol(self):
        super(S3StorageTest, self).standard_protocol()

    @utils.skipIfTravis
    def test_resizing_protocol(self):
        super(S3StorageTest, self).resizing_protocol()


class LocalStorageTest(BaseStorageTest):

    def setUp(self):  # NOQA
        self.incoming_storage = LocalStorage(os.environ['INCOMING_FOLDER'])
        self.active_storage = LocalStorage(os.environ['ACTIVE_FOLDER'])

    def test_standard_protocol(self):
        super(LocalStorageTest, self).standard_protocol()

    def test_resizing_protocol(self):
        super(LocalStorageTest, self).resizing_protocol()
