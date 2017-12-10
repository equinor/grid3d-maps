import os
import sys
import logging
import numpy as np

from xtgeo.common import XTGeoDialog
from xtgeo.surface import RegularSurface as RS

import xtgeo_grid3d_map_apps.grid3d_hc_thickness as xx
from .test_grid3d_hc_thickness2 import assert_equal, assert_almostequal

xtg = XTGeoDialog()

xtg = XTGeoDialog()
logger = xtg.basiclogger(__name__)

if not xtg._testsetup():
    sys.exit(-9)

td = xtg.tmpdir
testpath = xtg.testpath

# =============================================================================
# Do tests
# =============================================================================


def test_hc_thickness1a():
    """Test HC thickness with YAML config example 1a"""
    xx.main(['--config', 'tests/yaml/hc_thickness1a.yaml'])

    # now read in result and check avg value
    # x = RegularSurface('TMP/gull_1985_10_01.gri')
    # avg = float("{:4.3f}".format(float(x.values.mean())))
    # logger.info("AVG is " + str(avg))
    # assert avg == 3.649

    allz = RS(os.path.join(td, 'all--oilthickness--20010801_19991201.gri'))
    val = allz.values1d

    # -0.0574 in RMS volumetrics, but within range as different approach
    assert_almostequal(np.nanmean(val), -0.06269, 0.0001)
    assert_almostequal(np.nanstd(val), 0.301938, 0.0001)


def test_hc_thickness1b():
    """HC thickness with YAML config example 1b; zonation in own YAML file"""
    xx.main(['--config', 'tests/yaml/hc_thickness1b.yaml'])


def test_hc_thickness1c():
    """HC thickness with YAML config example 1c; no map settings"""
    xx.main(['--config', 'tests/yaml/hc_thickness1c.yaml'])
