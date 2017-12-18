import os
import sys
import pytest
import shutil
import glob

from xtgeo.common import XTGeoDialog
from xtgeo.surface import RegularSurface as RS

import xtgeo_grid3d_map_apps.grid3d_average_map as xx
from .test_grid3d_hc_thickness2 import assert_almostequal

xtg = XTGeoDialog()
logger = xtg.basiclogger(__name__)

if not xtg._testsetup():
    sys.exit(-9)

td = xtg.tmpdir
testpath = xtg.testpath

skiplargetest = pytest.mark.skipif(xtg.bigtest is False,
                                   reason="Big tests skip")

# =============================================================================
# Do tests
# =============================================================================


def test_average_map1a():
    """Test HC thickness with YAML config example 1a ECL based"""
    xx.main(['--config', 'tests/yaml/avg1a.yaml'])


def test_average_map1b():
    """Test HC thickness with YAML config example 1b ROFF based"""
    xx.main(['--config', 'tests/yaml/avg1b.yaml'])

    z1poro = RS(os.path.join(td, 'z1--avg1b_average_por.gri'))
    assert_almostequal(z1poro.values.mean(), 0.1598, 0.001, 'Mean value')
    assert_almostequal(z1poro.values.std(), 0.04, 0.003, 'Std. dev')

    imgs = glob.glob(os.path.join(td, '*avg1b*.png'))
    for img in imgs:
        shutil.copy2(img, 'docs/test_images/.')


def test_average_map1c():
    """Test HC thickness with YAML config example 1c ROFF based, rotated map"""
    xx.main(['--config', 'tests/yaml/avg1c.yaml'])

    z1poro = RS(os.path.join(td, 'all--avg1c_average_por.gri'))
    assert_almostequal(z1poro.values.mean(), 0.1678, 0.001, 'Mean value')