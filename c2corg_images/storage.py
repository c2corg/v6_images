import os
import datetime
import shutil
import threading
import boto3
import botocore

import logging
log = logging.getLogger(__name__)


EXPIRE_HOURS = 2


thread_data = threading.local()


def resources():
    if not hasattr(thread_data, 'resources'):
        thread_data.resources = {}
    return thread_data.resources


class BaseStorage():

    def keys(self):
        raise NotImplementedError()

    def exists(self, key):
        raise NotImplementedError()

    def get(self, key, path):
        raise NotImplementedError()

    def put(self, key, path):
        raise NotImplementedError()

    def delete(self, key):
        raise NotImplementedError()

    def copy(self, key, other_storage):
        raise NotImplementedError()

    def move(self, key, other_storage):
        raise NotImplementedError()


class S3Storage(BaseStorage):

    def __init__(self, bucket_name, endpoint_url=None):
        self._bucket_name = bucket_name
        self._endpoint_url = endpoint_url

    def resource(self):
        if self._endpoint_url not in resources():
            if self._endpoint_url is None:
                resource = boto3.resource('s3')
            else:
                resource = boto3.resource(
                    service_name='s3',
                    endpoint_url=self._endpoint_url)
                '''
                    ,
                    aws_access_key_id=None,
                    aws_secret_access_key=None,
                    config=botocore.config.Config(
                        s3={'addressing_style': 'path'},
                        signature_version=None  #'v2'  #'s3'  # botocore.UNSIGNED
                    )
                '''
                resource.meta.client.meta.events.unregister('before-sign.s3',
                                                            botocore.utils.fix_s3_host)
                resource.meta.client.meta.events.register('choose-signer.s3.*',
                                                          botocore.handlers.disable_signing)
            resources()[self._endpoint_url] = resource
        return resources()[self._endpoint_url]

    def bucket(self):
        return self.resource().Bucket(self._bucket_name)

    def object(self, key):
        return self.resource().Object(self._bucket_name, key)

    def keys(self):
        for object in self.bucket().objects.page_size(1000):
            yield object.key

    def exists(self, key):
        try:
            self.object(key).load()
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                return False
            else:
                raise e
        return True

    def get(self, key, path):
        self.object(key).download_file(path)

    def put(self, key, path):
        now = datetime.datetime.now()
        expires = now + datetime.timedelta(hours=EXPIRE_HOURS)
        self.bucket().upload_file(Filename=path,
                                  Key=key,
                                  ExtraArgs={'Expires': expires})

    def delete(self, key):
        self.object(key).delete()

    def copy(self, key, other_storage):
        if isinstance(other_storage, S3Storage):
            other_storage.object(key).copy_from(CopySource={
                'Bucket': self._bucket_name,
                'Key': key})
        elif isinstance(other_storage, LocalStorage):
            path = os.path.join(other_storage.path(), key)
            self.get(key, path)
        else:
            raise NotImplementedError()

    def move(self, key, other_storage):
        self.copy(key, other_storage)
        self.delete(key)


class LocalStorage(BaseStorage):

    def __init__(self, path):
        self._path = path
        if not os.path.isdir(self._path):
            os.makedirs(self._path)

    def path(self):
        return self._path

    def object_path(self, key):
        return os.path.abspath(os.path.join(self._path, key))

    def keys(self):
        return os.listdir(self._path)

    def exists(self, key):
        return os.path.isfile(self.object_path(key))

    def get(self, key, path):
        shutil.copyfile(self.object_path(key), path)

    def put(self, key, path):
        shutil.copyfile(path, self.object_path(key))

    def delete(self, key):
        os.unlink(self.object_path(key))

    def copy(self, key, other_storage):
        if isinstance(other_storage, LocalStorage):
            shutil.copyfile(self.object_path(key),
                            other_storage.object_path(key))
        elif isinstance(other_storage, S3Storage):
            other_storage.put(key, self.object_path(key))
        else:
            raise NotImplementedError()

    def move(self, key, other_storage):
        if isinstance(other_storage, LocalStorage):
            os.rename(self.object_path(key),
                      other_storage.object_path(key))
        elif isinstance(other_storage, S3Storage):
            other_storage.put(key, self.object_path(key))
            self.delete(key)


incoming_storage = None  # type: BaseStorage
active_storage = None  # type: BaseStorage
if os.environ['STORAGE_BACKEND'] == 's3':
    incoming_storage = S3Storage(os.environ['INCOMING_BUCKET'])
    active_storage = S3Storage(os.environ['ACTIVE_BUCKET'])
elif os.environ['STORAGE_BACKEND'] == 'local':
    incoming_storage = LocalStorage(os.environ['INCOMING_FOLDER'])
    active_storage = LocalStorage(os.environ['ACTIVE_FOLDER'])
else:
    raise Exception('STORAGE_BACKEND not supported or missing')

temp_storage = LocalStorage(os.path.join(os.environ['INCOMING_FOLDER'], 'temp'))
