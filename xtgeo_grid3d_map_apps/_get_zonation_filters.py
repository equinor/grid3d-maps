# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import

import sys
import os.path
import pprint
from collections import defaultdict
from collections import OrderedDict
import logging
import numpy as np
import numpy.ma as ma

from xtgeo.common import XTGeoDialog
from xtgeo.grid3d import Grid
from xtgeo.grid3d import GridProperties

xtg = XTGeoDialog()

# -----------------------------------------------------------------------------
# Logging setup
# -----------------------------------------------------------------------------

format = xtg.loggingformat

logging.basicConfig(format=format, stream=sys.stdout)
logging.getLogger().setLevel(xtg.logginglevel)

logger = logging.getLogger(__name__)


def zonation(config, dz):
    """Get the zonation, by either a file or a config spec"""

    zonation = np.zeros((dz.shape), dtype=np.int32) + 999

    # make azonation dictionary on the form
    # 'Tarbert: [1, 1]  # CHECK! note, inclusive?
    # 'Etive: [3, 4]
    # 'all': [1, 17]

    zoned = OrderedDict()

    if 'zranges' in config['zonation']:
        for i, zz in enumerate(config['zonation']['zranges']):
            zname = zz.keys()[0]
            intv = zz.values()[0]
            k01 = intv[0] - 1
            k02 = intv[1]

            logger.info('K01 K02: {} - {}'.format(k01, k02))

            zonation[:, :, k01: k02] = i + 1
            zoned[zname] = [i + 1, i + 1]
            zoned['all'] = [1, i + 1]

    else:
        zoned['all'] = [1, dz.shape[2]]
        zonation[:, :, :] = 1

    for myz, val in zoned.items():
        logger.info('Zonation list: {}: {}'.format(myz, val))

    logger.debug('Zonation matrix: {}\n'.format(zonation))

    try:
        zoned.move_to_end('all')
    except KeyError:
        pass
    except AttributeError:
        pass

    logger.info('The zoned dict: {}'.format(zoned))

    print(zonation[20, 20, 0:12])

    return zonation, zoned
