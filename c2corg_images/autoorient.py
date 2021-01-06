from c2corg_images.convert import transform
from c2cwsgiutils import stats

import logging
log = logging.getLogger(__name__)


def auto_orient(filename: str):
    log.info('Change image orientation image %s', filename)
    with stats.timer_context(['transform', 'auto_orient']):
        transform(filename, filename, ['-auto-orient'])
