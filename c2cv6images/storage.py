import shutil
import os
import boto3
import datetime

import logging
log = logging.getLogger(__name__)


EXPIRE_HOURS = 2


def send_local(path, key):
    """
    For testing locally or this Travis the file is directly activated.
    The file is copied to the active directory.
    :param path: The directory where the source file is stored.
    :param key: The filename of the image.
    """
    src = path + '/' + key
    target = 'active/' + key
    shutil.copyfile(src, target)


def send_s3(path, key):
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
        r = bucket.put_object(Key=key, Body=data, Expires=expires)


def send_and_unlink(path, key):
    backend = os.environ['STORAGE_BACKEND']
    if backend == 's3':
        send_s3(path, key)
    elif backend == 'local':
        send_local(path, key)
    else:
        raise 'Unhandled storage backend ' + backend
    os.unlink(path + '/' + key)
