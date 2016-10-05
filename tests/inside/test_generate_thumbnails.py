from c2corg_images.thumbnails import thumbnail_keys
from c2corg_images.storage import v5_storage, active_storage
from c2corg_images.scripts import generate_thumbnails

from tests import v5_key


def test_generate_thumbnails():
    key = v5_key
    v5_storage.copy(key, active_storage)
    for thumbnail in thumbnail_keys(key):
        v5_storage.copy(thumbnail, active_storage)

    mtimes = {}
    for thumbnail in thumbnail_keys(key):
        mtimes[thumbnail] = active_storage.last_modified(thumbnail)

    generate_thumbnails.generate_thumbnails()

    for key, value in mtimes.items():
        assert active_storage.last_modified(key) != value
