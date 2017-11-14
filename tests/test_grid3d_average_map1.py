import sys
import pytest

from xtgeo.common import XTGeoDialog

import xtgeo_grid3d_map_apps.grid3d_average_map as xx

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


def test_average_map1():
    """Test HC thickness with YAML config example 1"""
    xx.main(['--config', 'tests/yaml/avg1.yaml'])
