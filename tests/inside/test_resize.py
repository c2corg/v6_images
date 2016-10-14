from c2corg_images.resizing import resized_keys
from c2corg_images.storage import v5_storage, active_storage
from c2corg_images.scripts.resize import Resizer

from tests import v5_key


def test_resize():
    key = v5_key
    v5_storage.copy(key, active_storage)
    for resized in resized_keys(key):
        v5_storage.copy(resized, active_storage)

    mtimes = {}
    for resized in resized_keys(key):
        mtimes[resized] = active_storage.last_modified(resized)

    resizer = Resizer()
    resizer.execute()

    assert resizer.total == 1
    assert resizer.skipped == 0
    assert resizer.processed == 1
    assert resizer.errors == 0

    for key, value in mtimes.items():
        assert active_storage.last_modified(key) != value
