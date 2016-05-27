import pytest
import shutil

from c2corg_images.convert import create_thumbnail, rasterize_svg


@pytest.mark.parametrize("name,kind", [
    ('violin', 'jpg'), ('piano', 'png'), ('music', 'gif')
])
def test_create_thumbnail(name, kind):
    import os
    test_filename = 'tests/' + name + '.' + kind
    assert os.path.isfile(test_filename)

    # Copy test image to incoming directory
    original_filename = 'incoming/' + name + '.' + kind
    shutil.copyfile(test_filename, original_filename)
    assert os.path.isfile(original_filename)

    # Create thumbnail
    key = create_thumbnail('incoming', name, kind)

    # Check thumbnail exists
    created_file_mini = 'incoming/mini_' + key
    assert os.path.isfile(created_file_mini)
    assert os.stat(created_file_mini).st_size < os.stat(original_filename).st_size


def test_rasterize_svg():
    import os
    name = 'pipe_organ'
    test_filename = 'tests/' + name + '.svg'
    assert os.path.isfile(test_filename)

    target_filename = 'incoming/' + name + '.png'
    rasterize_svg(test_filename, target_filename)

    # Check png exists
    assert os.path.isfile(target_filename)
