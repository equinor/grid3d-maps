import os
import sys
import logging

from xtgeo.common import XTGeoDialog

import xtgeo_grid3d_map_apps.grid3d_hc_thickness as xx

xtg = XTGeoDialog()

path = 'TMP'
try:
    os.makedirs(path)
except OSError:
    if not os.path.isdir(path):
        raise

logging.basicConfig(format=xtg.loggingformat, stream=sys.stdout)
logging.getLogger().setLevel(xtg.logginglevel)

logger = logging.getLogger(__name__)

# =============================================================================
# Do tests
# =============================================================================


def test_hc_thickness1():
    """Test HC thickness with YAML config example 1"""
    xx.main(['--config', 'tests/yaml/hc_thickness1.yaml'])

    # now read in result and check avg value
    # x = RegularSurface('TMP/gull_1985_10_01.gri')
    # avg = float("{:4.3f}".format(float(x.values.mean())))
    # logger.info("AVG is " + str(avg))
    # assert avg == 3.649


def test_hc_thickness2():
    """HC thickness with YAML config example 2; zonation in own YAML file"""
    xx.main(['--config', 'tests/yaml/hc_thickness2.yaml'])
