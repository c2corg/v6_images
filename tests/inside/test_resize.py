from c2corg_images.resizing import resized_keys
from c2corg_images.storage import active_storage
from c2corg_images.scripts.resize import Resizer

import os
import shutil
from tests import data_folder, v5_key


def test_resize():
    # clear active storage
    for key in active_storage.keys():
        active_storage.delete(key)

    # put some file in active storage
    key = v5_key
    shutil.copyfile(os.path.join(data_folder, 'v5_images', v5_key),
                    active_storage.object_path(v5_key))
    for resized in resized_keys(key):
        shutil.copyfile(os.path.join(data_folder, 'v5_images', resized),
                        active_storage.object_path(resized))

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
