# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import

import sys
from collections import OrderedDict
import logging
import numpy as np

from xtgeo.common import XTGeoDialog

xtg = XTGeoDialog()
format = xtg.loggingformat

logging.basicConfig(format=format, stream=sys.stdout)
logging.getLogger().setLevel(xtg.logginglevel)

logger = logging.getLogger(__name__)


def zonation(config, dz):
    """Get the zonations, by either a file (TODO) or a config spec

    The super zonation is a collection of zones, whcih do not need to be
    in sequence.

    Args:
        The config dict, the dz property object (just as a proxy)

    Returns:
        zonation (np): zonation, 3D numpy
        zoned (dict): Zonation dictionary (name: zone number)
        superzoned (dict): Super zonation dictionary (name: [zone range])
    """

    zonation = np.zeros((dz.shape), dtype=np.int32, order='F')

    # make azonation dictionary on the form
    # 'Tarbert: [1, 1]  # CHECK! note, inclusive?
    # 'Etive: [3, 4]
    # 'all': [1, 17]

    zoned = OrderedDict()
    superzoned = OrderedDict()

    if 'zranges' in config['zonation']:
        for i, zz in enumerate(config['zonation']['zranges']):
            zname = zz.keys()[0]
            intv = zz.values()[0]
            k01 = intv[0] - 1
            k02 = intv[1]

            logger.info('K01 K02: {} - {}'.format(k01, k02))

            zonation[:, :, k01: k02] = i + 1
            zoned[zname] = i + 1

    if 'superranges' in config['zonation']:
        logger.info('Found superranges keyword...')
        for i, zz in enumerate(config['zonation']['superranges']):
            zname = zz.keys()[0]
            superzoned[zname] = []
            intv = zz.values()[0]
            logger.debug('Superzone spec no {}: {}  {}'
                         .format(i + 1, zname, intv))
            for zn in intv:
                superzoned[zname].append(zoned[zn])

    for myz, val in zoned.items():
        logger.info('Zonation list: {}: {}'.format(myz, val))

    logger.debug('Zonation in cell 1, 1, kmin:kmax: {}'
                 .format(zonation[0, 0, :]))

    for key, vals in superzoned.items():
        logger.debug('Superzoned {}  {}'.format(key, vals))

    logger.info('The zoned dict: {}'.format(zoned))
    logger.info('The superzoned dict: {}'.format(superzoned))

    zmerged = zoned.copy()
    zmerged.update(superzoned)

    zmerged['all'] = None

    logger.info('The merged dict: {}'.format(zmerged))

    return zonation, zmerged
