import os
import unittest
from c2corg_images.storage import S3Storage, LocalStorage, temp_storage  # , v5_storage
from tests import utils, data_folder

import logging
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('s3transfer').setLevel(logging.CRITICAL)

key = 'test.png'
source_file = os.path.join(data_folder, 'piano.png')


class BaseStorageTest(unittest.TestCase):

    def standard_protocol(self):
        # put file in temp storage for processing
        temp_storage.put(key, source_file)

        # move it in incoming storage waiting for publication
        temp_storage.move(key, self.incoming_storage)
        assert self.incoming_storage.exists(key)
        assert not temp_storage.exists(key)

        # on publishing it is moved to active storage
        self.incoming_storage.move(key, self.active_storage)
        assert self.active_storage.exists(key)
        assert not self.incoming_storage.exists(key)

        # cleaning
        self.active_storage.delete(key)
        assert not self.active_storage.exists(key)

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
        self.incoming_storage = S3Storage(os.environ['INCOMING_BUCKET'])
        self.active_storage = S3Storage(os.environ['ACTIVE_BUCKET'])

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
