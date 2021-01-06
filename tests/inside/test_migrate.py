from unittest.mock import patch, Mock
from c2corg_images.resizing import resized_keys
from c2corg_images.storage import active_storage
from c2corg_images.scripts.migrate import Migrator

files = [{'filename': '1437737998_1507635670.jpg', 'has_svg': False},
         {'filename': '1274781175_1003161687.jpg', 'has_svg': True}]


sql_results = (
    [
        None,  # _init_v5_database
        None,  # _init_bucket_database
        Mock(fetchone=Mock(return_value={'count': 2})),
        files] +
    4 * [Mock(fetchone=Mock(return_value={'count': 0}))] +  # _is_migrated
    4 * [Mock(fetchone=Mock(return_value={'count': 0})),  # _is_migrated
         None] +  # _set_migrated
    4 * [Mock(fetchone=Mock(return_value={'count': 0}))] +  # _is_migrated
    4 * [Mock(fetchone=Mock(return_value={'count': 0})),  # _is_migrated
         None] +  # _set_migrated
    [
        Mock(fetchone=Mock(return_value={'count': 2})),
        files] +
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
    migrator.execute(jobs=1)

    assert migrator.total == 2
    assert migrator.skipped == 0
    assert migrator.processed == 2
    assert migrator.errors == 0

    for key in [file['filename'] for file in files]:
        if key == '1274781175_1003161687.jpg':
            assert active_storage.exists('1274781175_1003161687.svg')
        else:
            assert active_storage.exists(key)
        for resized in resized_keys(key):
            assert active_storage.exists(resized)

    migrator.execute()

    assert migrator.total == 2
    assert migrator.skipped == 2
    assert migrator.processed == 0
    assert migrator.errors == 0
