# On Debian, you need to install these packages:
# jpegoptim optipng pngcrush advancecomp

import subprocess
from os.path import splitext

import logging
log = logging.getLogger(__name__)


def create_thumbnail(path, key):
    target_key = 'mini_' + key
    original_file = path + '/' + key
    target_file = path + '/' + target_key

    log.info('Creating thumbnail for %s', key)
    args = ['scripts/resize.sh', original_file, target_file]

    print(args)
    subprocess.check_call(args)

    optimize(path, target_key)

    return target_key


def optimize(path, key):
    target_file = path + '/' + key
    ext = splitext(key)[1].lower()
    cmd = ['scripts/optimize%s.sh' % ext, target_file]
    print(cmd)
    subprocess.check_call(cmd, shell=True)
