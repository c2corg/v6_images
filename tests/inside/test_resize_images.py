from c2corg_images.resizing import resized_keys
from c2corg_images.storage import v5_storage, active_storage
from c2corg_images.scripts import resize_images

from tests import v5_key


def test_resize_images():
    key = v5_key
    v5_storage.copy(key, active_storage)
    for resized in resized_keys(key):
        v5_storage.copy(resized, active_storage)

    mtimes = {}
    for resized in resized_keys(key):
        mtimes[resized] = active_storage.last_modified(resized)

    resize_images.resize_images()

    for key, value in mtimes.items():
        assert active_storage.last_modified(key) != value
