import os
import sys
from pathlib import Path
import pytest
import numpy as np

from xtgeo.common import XTGeoDialog
import xtgeo

import xtgeoapp_grd3dmaps.avghc.grid3d_hc_thickness as xx

xtg = XTGeoDialog()

xtg = XTGeoDialog()
logger = xtg.basiclogger(__name__)

if not xtg.testsetup():
    sys.exit(-9)

TMPD = xtg.tmpdir
testpath = xtg.testpath


def test_hc_thickness2a():
    """HC thickness with YAML config example 2a; use STOOIP prop from RMS"""
    os.chdir(str(Path(__file__).absolute().parent.parent))
    xx.main(["--config", "tests/yaml/hc_thickness2a.yml"])

    # read in result and check statistical values

    allz = xtgeo.surface_from_file(
        os.path.join(TMPD, "all--stoiip_oilthickness--19900101.gri")
    )

    val = allz.values1d
    val[val <= 0] = np.nan

    # compared with data from RMS:
    assert np.nanmean(val) == pytest.approx(1.9521, abs=0.01)
    assert np.nanstd(val) == pytest.approx(1.2873, abs=0.01)
