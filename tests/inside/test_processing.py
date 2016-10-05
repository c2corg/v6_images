import os
import pytest
import shutil

from c2corg_images import THUMBNAIL_CONFIGS
from c2corg_images.convert import rasterize_svg
from c2corg_images.thumbnails import create_thumbnail
from c2corg_images.storage import temp_storage

from tests import data_folder


@pytest.mark.parametrize("filename", [
    'violin.jpg', 'piano.png', 'music.gif'
])
def test_create_thumbnail(filename):
    test_filename = os.path.join(data_folder, filename)
    assert os.path.isfile(test_filename)

    # Copy test image to incoming directory
    original_filename = temp_storage.object_path(filename)
    shutil.copyfile(test_filename, original_filename)
    assert os.path.isfile(original_filename)

    # Create thumbnails
    for config in THUMBNAIL_CONFIGS:
        thumbnail = create_thumbnail(temp_storage.path(), filename, config)
        assert os.path.isfile(temp_storage.object_path(thumbnail))
        # assert os.stat(created_thumbnail).st_size < os.stat(original_filename).st_size, config


def test_rasterize_svg():
    name = 'pipe_organ'
    test_filename = 'tests/' + name + '.svg'
    assert os.path.isfile(test_filename)

    target_filename = 'incoming/' + name + '.png'
    rasterize_svg(test_filename, target_filename)

    # Check png exists
    assert os.path.isfile(target_filename)
