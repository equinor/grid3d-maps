import os
import sys
import logging

from xtgeo.surface import RegularSurface
from xtgeo.common import XTGeoDialog

import xtgeo_grid3d_map_apps.grid3d_hc_thickness as xx

xtg = XTGeoDialog()

path = 'TMP'
try:
    os.makedirs(path)
except OSError:
    if not os.path.isdir(path):
        raise

# =============================================================================
# Do tests
# =============================================================================


def getlogger(name):

    format = xtg.loggingformat

    logging.basicConfig(format=format, stream=sys.stdout)
    logging.getLogger().setLevel(xtg.logginglevel)  # root logger!

    return logging.getLogger(name)


def test_hc_thickness1():
    logger = getlogger('test_hc_thickness1')

    xx.main(['--config', 'tests/yaml/hc_thickness1.yaml'])

    # now read in result and check avg value
    # x = RegularSurface('TMP/gull_1985_10_01.gri')
    # avg = float("{:4.3f}".format(float(x.values.mean())))
    # logger.info("AVG is " + str(avg))
    # assert avg == 3.649
