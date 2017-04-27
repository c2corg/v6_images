import os
import pytest
import shutil
from PIL import Image

from c2corg_images import RESIZING_CONFIG
from c2corg_images.convert import rasterize_svg
from c2corg_images.cropping import create_cropped_image
from c2corg_images.resizing import create_resized_image
from c2corg_images.storage import temp_storage

from tests import data_folder


def _copy_file_to_temp_storage(filename):
    test_filename = os.path.join(data_folder, 'images', filename)
    assert os.path.isfile(test_filename)
    temp_filename = temp_storage.object_path(filename)
    shutil.copyfile(test_filename, temp_filename)
    assert os.path.isfile(temp_filename)


@pytest.mark.parametrize("filename", [
    'violin.jpg', 'piano.png', 'music.gif'
])
def test_create_resized_image(filename):
    _copy_file_to_temp_storage(filename)
    for config in RESIZING_CONFIG:
        resized = create_resized_image(temp_storage.path(), filename, config)
        assert os.path.isfile(temp_storage.object_path(resized))


@pytest.mark.parametrize("filename", [
    'violin.jpg', 'piano.png', 'music.gif'
])
def test_create_cropped_image(filename):
    _copy_file_to_temp_storage(filename)
    crop_options = '200x100+10+20'
    create_cropped_image(temp_storage.path(), filename, crop_options)
    result_path = temp_storage.object_path(filename)
    assert os.path.isfile(result_path)
    image = Image.open(result_path)
    assert image.size == (200, 100)


def test_rasterize_svg():
    name = 'pipe_organ'
    svg_path = os.path.join(data_folder, 'images', "{}.svg".format(name))
    assert os.path.isfile(svg_path)

    png_path = temp_storage.object_path("{}.png".format(name))
    rasterize_svg(svg_path, png_path)

    # Check png exists
    assert os.path.isfile(png_path)
