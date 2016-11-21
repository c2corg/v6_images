from unittest.mock import patch, Mock
from c2corg_images.resizing import resized_keys
from c2corg_images.storage import active_storage
from c2corg_images.scripts.migrate import Migrator

key1 = '1437737998_1507635670.jpg'
key2 = '1437738073_375759438.jpg'


sql_results = (
    [
        None,  # _init_v5_database
        None,  # _init_bucket_database
        Mock(fetchone=Mock(return_value={'count': 2})),
        [{'filename': key1}, {'filename': key2}]] +
    8 * [Mock(fetchone=Mock(return_value={'count': 0}))] +  # _is_migrated
    8 * [None] +  # _set_migrated
    [
        Mock(fetchone=Mock(return_value={'count': 2})),
        [{'filename': key1}, {'filename': key2}]] +
    8 * [Mock(fetchone=Mock(return_value={'count': 1}))])  # _is_migrated


@patch(
    'c2corg_images.scripts.migrate.create_engine',
    return_value=Mock(
        connect=Mock(
            return_value=Mock(
                execute=Mock(
                    side_effect=sql_results)))))
def test_migrate(create_engine):
    migrator = Migrator()
    migrator.execute()

    assert migrator.total == 2
    assert migrator.skipped == 0
    assert migrator.processed == 2
    assert migrator.errors == 0

    for key in (key1, key2):
        assert active_storage.exists(key)
        for resized in resized_keys(key):
            assert active_storage.exists(resized)

    migrator.execute()

    assert migrator.total == 2
    assert migrator.skipped == 2
    assert migrator.processed == 0
    assert migrator.errors == 0
