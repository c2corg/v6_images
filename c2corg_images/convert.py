import subprocess
from typing import List

import logging
log = logging.getLogger(__name__)


def rasterize_svg(svgfile: str, pngfile: str):
    log.info('Rasterizing SVG %s', svgfile)
    args = ['scripts/rasterize.sh', svgfile, pngfile]
    subprocess.check_call(args)


def transform(original_file: str, target_file: str, options: List[str]):
    cmd = ['convert', original_file] + options + [target_file]
    subprocess.check_call(cmd)
