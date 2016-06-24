import shutil
import os
import boto3
import datetime

import logging
log = logging.getLogger(__name__)


EXPIRE_HOURS = 2


def send_local(path: str, key: str):
    """
    For testing locally or this Travis the file is directly activated.
    The file is copied to the active directory.
    :param path: The directory where the source file is stored.
    :param key: The filename of the image.
    """
    src = os.path.join(path, key)
    target = os.path.join(os.environ['ACTIVE_FOLDER'], key)
    shutil.copyfile(src, target)


def send_s3(path: str, key: str):
    """
    For production, the file is sent to a private S3 bucket, with an
    expiration of 2 hours. The file must be activated by the API (moved to
    the public bucket) before the expiration.
    :param path: The directory where the source file is stored.
    :param key: The filename of the image.
    """
    incoming_bucket_name = os.environ['INCOMING_BUCKET']
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(incoming_bucket_name)
    now = datetime.datetime.now()
    expires = now + datetime.timedelta(hours=EXPIRE_HOURS)
    with open(path + '/' + key, 'rb') as data:
        bucket.put_object(Key=key, Body=data, Expires=expires)


def publish_s3(key: str):
    incoming_bucket_name = os.environ['INCOMING_BUCKET']
    active_bucket_name = os.environ['ACTIVE_BUCKET']
    s3 = boto3.resource('s3')
    s3.Object(active_bucket_name, key).copy_from(
        CopySource='{}/{}'.format(incoming_bucket_name, key))
    s3.Object(incoming_bucket_name, key).delete()


def send_and_unlink(path: str, key: str):
    backend = os.environ['STORAGE_BACKEND']
    if backend == 's3':
        send_s3(path, key)
    elif backend == 'local':
        send_local(path, key)
    else:
        raise Exception('Unhandled storage backend ' + backend)
    os.unlink(path + '/' + key)


def publish(key: str):
    backend = os.environ['STORAGE_BACKEND']
    if backend == 's3':
        publish_s3(key)
    elif backend == 'local':
        pass
    else:
        raise Exception('Unhandled storage backend ' + backend)
