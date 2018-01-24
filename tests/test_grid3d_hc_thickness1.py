import os
import sys
import shutil
import glob
import warnings

import numpy as np

from xtgeo.common import XTGeoDialog
from xtgeo.surface import RegularSurface as RS

import xtgeo_grid3d_map_apps.grid3d_hc_thickness as xx
from .test_grid3d_hc_thickness2 import assert_almostequal

xtg = XTGeoDialog()

xtg = XTGeoDialog()
logger = xtg.basiclogger(__name__)

if not xtg.testsetup():
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
    assert_almostequal(np.nanmean(val), -0.06269, 0.001)
    assert_almostequal(np.nanstd(val), 0.303, 0.001)


def test_hc_thickness1b():
    """HC thickness with YAML config example 1b; zonation in own YAML file"""
    xx.main(['--config', 'tests/yaml/hc_thickness1b.yaml'])
    imgs = glob.glob(os.path.join(td, '*hc1b*.png'))
    print(imgs)
    for img in imgs:
        shutil.copy2(img, 'docs/test_images/.')


def test_hc_thickness1c():
    """HC thickness with YAML config example 1c; no map settings"""
    xx.main(['--config', 'tests/yaml/hc_thickness1c.yaml'])


def test_hc_thickness1d():
    """HC thickness with YAML config example 1d; as 1c but use_porv instead"""
    warnings.simplefilter('error')
    xx.main(['--config', 'tests/yaml/hc_thickness1d.yaml'])

    x1d = RS(os.path.join(td, 'all--hc1d_oilthickness--19991201.gri'))

    assert_almostequal(x1d.values.mean(), 0.516, 0.001)


def test_hc_thickness1e():
    """HC thickness with YAML config 1e; as 1d but use ROFF grid input"""
    xx.main(['--config', 'tests/yaml/hc_thickness1e.yaml'])

    x1e = RS(os.path.join(td, 'all--hc1e_oilthickness--19991201.gri'))
    logger.info(x1e.values.mean())
    assert_almostequal(x1e.values.mean(), 0.516, 0.001)


def test_hc_thickness1f():
    """HC thickness with YAML config 1f; use rotated template map"""
    xx.main(['--config', 'tests/yaml/hc_thickness1f.yaml'])

    x1f = RS(os.path.join(td, 'all--hc1f_oilthickness--19991201.gri'))
    logger.info(x1f.values.mean())
    # other mean as the map is smaller; checked in RMS
    assert_almostequal(x1f.values.mean(), 1.0999, 0.0001)


def test_hc_thickness1g():
    """HC thickness with YAML config 1g; use rotated template map and both
    oil and gas"""
    xx.main(['--config', 'tests/yaml/hc_thickness1g.yaml'])

    x1g1 = RS(os.path.join(td, 'all--hc1g_oilthickness--19991201.gri'))
    logger.info(x1g1.values.mean())
    assert_almostequal(x1g1.values.mean(), 1.0999, 0.0001)

    x1g2 = RS(os.path.join(td, 'all--hc1g_gasthickness--19991201.gri'))
    logger.info(x1g1.values.mean())
    assert_almostequal(x1g2.values.mean(), 0.000, 0.0001)
