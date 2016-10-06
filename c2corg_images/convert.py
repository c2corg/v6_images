import subprocess
from typing import List

import logging
log = logging.getLogger(__name__)


def rasterize_svg(svgfile: str, jpgfile: str):
    log.info('Rasterizing SVG %s', svgfile)
    cmd = ['rsvg-convert', '-b', 'white', svgfile, '-o', jpgfile]
    log.debug(' '.join(cmd))
    subprocess.check_call(cmd)


def transform(original_file: str, target_file: str, options: List[str]):
    cmd = ['convert', original_file] + options + [target_file]
    log.debug(' '.join(cmd))
    subprocess.check_call(cmd)
