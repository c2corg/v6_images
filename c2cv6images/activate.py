import shutil
import os

import logging
log = logging.getLogger(__name__)


def send(path, key):
    src = path + '/' + key
    target = 'active/' + key
    shutil.copyfile(src, target)
    os.unlink(src)


def activate_key(path, key):
    log.debug('Activating ' + key)
    send(path, key)
    send(path, '/mini_' + key)
    log.debug('Done activating ' + key)
