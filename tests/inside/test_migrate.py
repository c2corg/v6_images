from c2corg_images.resizing import resized_keys
from c2corg_images.storage import active_storage
from c2corg_images.scripts import migrate

from tests import v5_key


def test_migrate():
    migrate.migrate()

    assert active_storage.exists(v5_key)
    for resized in resized_keys(v5_key):
        assert active_storage.exists(resized)

    assert migrate.migrate() == 0
