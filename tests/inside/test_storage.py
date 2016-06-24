import os
import shutil
import tempfile
from tests import utils

from c2corg_images.storage import send_local, send_s3, publish_s3


def test_send_local():
    with tempfile.NamedTemporaryFile(suffix='.png') as tmp_file:
        shutil.copyfile('tests/piano.png', tmp_file.name)

        dirname = os.path.dirname(tmp_file.name)
        filename = os.path.basename(tmp_file.name)
        send_local(dirname, filename)

        assert os.path.isfile('active/' + filename)


@utils.skipIfTravis
def test_s3():
    with tempfile.NamedTemporaryFile(suffix='.png') as tmp_file:
        shutil.copyfile('tests/piano.png', tmp_file.name)

        dirname = os.path.dirname(tmp_file.name)
        filename = os.path.basename(tmp_file.name)
        send_s3(dirname, filename)

        publish_s3(filename)
