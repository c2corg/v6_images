import os
import pytest
import shutil

from c2corg_images import RESIZING_CONFIG
from c2corg_images.convert import rasterize_svg
from c2corg_images.resizing import create_resized_image
from c2corg_images.storage import temp_storage

from tests import data_folder


@pytest.mark.parametrize("filename", [
    'violin.jpg', 'piano.png', 'music.gif'
])
def test_create_resized_image(filename):
    test_filename = os.path.join(data_folder, 'images', filename)
    assert os.path.isfile(test_filename)

    # Copy test image to incoming directory
    original_filename = temp_storage.object_path(filename)
    shutil.copyfile(test_filename, original_filename)
    assert os.path.isfile(original_filename)

    # Create resized image
    for config in RESIZING_CONFIG:
        resized = create_resized_image(temp_storage.path(), filename, config)
        assert os.path.isfile(temp_storage.object_path(resized))
        # assert os.stat(created_resized_images).st_size < os.stat(original_filename).st_size, config


def test_rasterize_svg():
    name = 'pipe_organ'
    svg_path = os.path.join(data_folder, 'images', "{}.svg".format(name))
    assert os.path.isfile(svg_path)

    png_path = temp_storage.object_path("{}.png".format(name))
    rasterize_svg(svg_path, png_path)

    # Check png exists
    assert os.path.isfile(png_path)
