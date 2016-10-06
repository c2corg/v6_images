import os
import subprocess
from wand.image import Image

import logging
log = logging.getLogger(__name__)


def rasterize_svg(svgfile: str, pngfile: str):
    log.info('Rasterizing SVG %s', svgfile)
    args = ['scripts/rasterize.sh', svgfile, pngfile]
    subprocess.check_call(args)


def transform(original_file: str, target_file: str, geometry: str):
    with Image(filename=original_file) as image:
        with image.clone() as i:
            i.type = image.type
            i.alpha_channel = image.alpha_channel
            i.transform(resize=geometry)
            i.save(filename=target_file)


def optimize(filename: str):
    base, ext = os.path.splitext(filename)
    cmd = ['scripts/optimize{}.sh'.format(ext), filename]
    subprocess.check_call(cmd)
