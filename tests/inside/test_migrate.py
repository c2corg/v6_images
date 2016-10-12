from c2corg_images.resizing import resized_keys
from c2corg_images.storage import active_storage
from c2corg_images.scripts.migrate import Migrator

from tests import v5_key


def test_migrate():
    migrator = Migrator()
    migrator.execute()

    assert migrator.total == 1
    assert migrator.skipped == 0
    assert migrator.processed == 1
    assert migrator.errors == 0

    assert active_storage.exists(v5_key)
    for resized in resized_keys(v5_key):
        assert active_storage.exists(resized)

    migrator.execute()

    assert migrator.total == 1
    assert migrator.skipped == 1
    assert migrator.processed == 0
    assert migrator.errors == 0
