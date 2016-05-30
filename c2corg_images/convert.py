import subprocess
from wand.image import Image

import logging
log = logging.getLogger(__name__)


def rasterize_svg(svgfile, pngfile):
    log.info('Rasterizing SVG %s', svgfile)
    args = ['scripts/rasterize.sh', svgfile, pngfile]
    subprocess.check_call(args)


def transform(original_file, target_file, geometry):
    with Image(filename=original_file) as image:
        with image.clone() as i:
            i.type = image.type
            i.alpha_channel = image.alpha_channel
            i.transform(resize=geometry)
            i.save(filename=target_file)


def format_config_template(path, pre_key, kind, template):
    return template \
        .replace('%(base)', path + '/' + pre_key) \
        .replace('%(kind)', kind)


def create_thumbnail(path, pre_key, kind, config):
    key = '%s.%s' % (pre_key, kind)
    original_file = path + '/' + key
    target_file = format_config_template(path, pre_key, kind, config['template'])

    log.info('Creating thumbnail for %s in %s', key, target_file)
    transform(original_file, target_file, config['geometry'])

    optimize(target_file, kind)

    return target_file


def optimize(filename, kind):
    cmd = ['scripts/optimize.%s.sh' % kind, filename]
    subprocess.check_call(cmd)
