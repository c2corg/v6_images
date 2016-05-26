import shutil
import os

import logging
log = logging.getLogger(__name__)


def send(path, key):
    src = path + '/' + key
    target = 'active/' + key
    shutil.copyfile(src, target)
    os.unlink(src)
