import os
import datetime
import shutil
import threading
import boto3
import botocore
import mimetypes
from c2cwsgiutils import stats
import typing  # noqa

import logging
log = logging.getLogger(__name__)


EXPIRE_HOURS = 2
PAGE_SIZE = 1000
S3_SIGNATURE_VERSION = os.environ.get('S3_SIGNATURE_VERSION', 's3v4')
S3_CONFIG = botocore.config.Config(signature_version=S3_SIGNATURE_VERSION)


thread_data = threading.local()


def session():
    if not hasattr(thread_data, 'session'):
        thread_data.session = boto3.session.Session()
    return thread_data.session


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

    def last_modified(self, key):
        raise NotImplementedError()


class S3Storage(BaseStorage):

    def __init__(self, bucket_name, params={}, default_acl=None, should_expire=None):
        self._bucket_name = bucket_name
        self._params = params
        self._endpoint_url = self._params.get('endpoint_url', None)
        self._should_expire = should_expire
        self.default_acl = default_acl

    def resource(self):
        if self._endpoint_url not in resources():
            if self._endpoint_url is None:
                resource = session().resource('s3', config=S3_CONFIG)
            else:
                resource = session().resource(
                    service_name='s3',
                    **self._params)
                resource.meta.client.meta.events.unregister('before-sign.s3',
                                                            botocore.utils.fix_s3_host)
                '''
                resource.meta.client.meta.events.register('choose-signer.s3.*',
                                                          botocore.handlers.disable_signing)
                '''
            resources()[self._endpoint_url] = resource
        return resources()[self._endpoint_url]

    def bucket(self):
        return self.resource().Bucket(self._bucket_name)

    def object(self, key):
        return self.resource().Object(self._bucket_name, key)

    def keys(self):
        for object in self.bucket().objects.page_size(PAGE_SIZE):
            yield object.key

    def exists(self, key):
        try:
            with stats.timer_context(['storage', 's3', 'exists']):
                object = self.object(key)
                object.load()

                mimetype = mimetypes.guess_type(key)[0]
                if object.content_type != mimetype:
                    object.copy_from(
                        ACL=self.default_acl,
                        ContentType=mimetype,
                        CopySource={
                            'Bucket': self._bucket_name,
                            'Key': key
                        }
                    )
                return True

        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                return False
            else:
                raise e
        return True

    def get(self, key, path):
        with stats.timer_context(['storage', 's3', 'get']):
            self.object(key).download_file(path)

    def put(self, key, path):
        with open(path, 'rb') as file:
            kwargs = {}
            if self._should_expire:
                now = datetime.datetime.now()
                expires = now + datetime.timedelta(hours=EXPIRE_HOURS)
                kwargs['Expires'] = expires
            with stats.timer_context(['storage', 's3', 'put']):
                self.bucket().put_object(
                    ACL=self.default_acl,
                    Body=file,
                    ContentType=mimetypes.guess_type(key)[0],
                    Key=key,
                    **kwargs)

    def delete(self, key):
        with stats.timer_context(['storage', 's3', 'delete']):
            self.object(key).delete()

    def copy(self, key, other_storage):
        with stats.timer_context(['storage', 's3', 'copy']):
            if isinstance(other_storage, S3Storage):
                new_object = other_storage.object(key)
                new_object.copy_from(
                    ACL=other_storage.default_acl,
                    ContentType=mimetypes.guess_type(key)[0],
                    CopySource={
                        'Bucket': self._bucket_name,
                        'Key': key})
            elif isinstance(other_storage, LocalStorage):
                path = os.path.join(other_storage.path(), key)
                self.get(key, path)
            else:
                raise NotImplementedError()

    def move(self, key, other_storage):
        with stats.timer_context(['storage', 's3', 'move']):
            self.copy(key, other_storage)
            self.delete(key)

    def last_modified(self, key):
        with stats.timer_context(['storage', 's3', 'last_modified']):
            return self.object(key).last_modified


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
        if not self.exists(key):
            return
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

    def last_modified(self, key):
        return datetime.datetime.fromtimestamp(os.path.getmtime(self.object_path(key)))


def getS3Params(prefix):
    params = {}
    PREFIX = os.environ.get("{}_PREFIX".format(prefix), False)
    if PREFIX:
        params['endpoint_url'] = os.environ.get("{}_ENDPOINT".format(PREFIX), False)
        params['config'] = S3_CONFIG
        params['aws_access_key_id'] = os.environ.get("{}_ACCESS_KEY_ID".format(PREFIX))
        params['aws_secret_access_key'] = os.environ.get("{}_SECRET_KEY".format(PREFIX))

    return params


incoming_storage = None  # type: typing.Optional[BaseStorage]
active_storage = None  # type: typing.Optional[BaseStorage]
if os.environ['STORAGE_BACKEND'] == 's3':
    incoming_storage = S3Storage(os.environ['INCOMING_BUCKET'],
                                 getS3Params('INCOMING'),
                                 default_acl='private',
                                 should_expire=True)
    active_storage = S3Storage(os.environ['ACTIVE_BUCKET'],
                               getS3Params('ACTIVE'),
                               default_acl='public-read')
elif os.environ['STORAGE_BACKEND'] == 'local':
    incoming_storage = LocalStorage(os.environ['INCOMING_FOLDER'])
    active_storage = LocalStorage(os.environ['ACTIVE_FOLDER'])
else:
    raise Exception('STORAGE_BACKEND not supported or missing')

temp_storage = LocalStorage(os.environ['TEMP_FOLDER'])
