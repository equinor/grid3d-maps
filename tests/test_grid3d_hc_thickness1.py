import os
import shutil
import glob
import warnings
from pathlib import Path

import numpy as np
import pytest

import xtgeo
from xtgeo.common import XTGeoDialog

import xtgeoapp_grd3dmaps.avghc.grid3d_hc_thickness as xx

xtg = XTGeoDialog()

xtg = XTGeoDialog()
logger = xtg.basiclogger(__name__)

if not xtg.testsetup():
    raise SystemExit

TMPD = xtg.tmpdir
testpath = xtg.testpath
ojoin = os.path.join

# =============================================================================
# Do tests
# =============================================================================


def test_hc_thickness1a():
    """Test HC thickness with YAML config example 1a"""
    os.chdir(str(Path(__file__).absolute().parent.parent))
    dmp = ojoin(TMPD, "hc1a_dump.yml")
    xx.main(["--config", "tests/yaml/hc_thickness1a.yml", "--dump", dmp])

    allz = xtgeo.surface_from_file(
        ojoin(TMPD, "all--oilthickness--20010101_19991201.gri")
    )
    val = allz.values1d

    print(np.nanmean(val), np.nanstd(val))

    # -0.0574 in RMS volumetrics, but within range as different approach
    assert np.nanmean(val) == pytest.approx(-0.03653, 0.001)
    assert np.nanstd(val) == pytest.approx(0.199886, 0.001)


def test_hc_thickness1b():
    """HC thickness with YAML config example 1b; zonation in own YAML file"""
    os.chdir(str(Path(__file__).absolute().parent.parent))
    xx.main(["--config", "tests/yaml/hc_thickness1b.yml"])
    imgs = glob.glob(ojoin(TMPD, "*hc1b*.png"))
    print(imgs)
    for img in imgs:
        shutil.copy2(img, "docs/test_images/.")


def test_hc_thickness1c():
    """HC thickness with YAML config example 1c; no map settings"""
    os.chdir(str(Path(__file__).absolute().parent.parent))
    xx.main(["--config", "tests/yaml/hc_thickness1c.yml"])


def test_hc_thickness1d():
    """HC thickness with YAML config example 1d; as 1c but use_porv instead"""
    os.chdir(str(Path(__file__).absolute().parent.parent))
    warnings.simplefilter("error")
    xx.main(["--config", "tests/yaml/hc_thickness1d.yml"])

    x1d = xtgeo.surface_from_file(ojoin(TMPD, "all--hc1d_oilthickness--19991201.gri"))

    assert x1d.values.mean() == pytest.approx(0.516, abs=0.001)


def test_hc_thickness1e():
    """HC thickness with YAML config 1e; as 1d but use ROFF grid input"""
    os.chdir(str(Path(__file__).absolute().parent.parent))
    xx.main(["--config", "tests/yaml/hc_thickness1e.yml"])

    x1e = xtgeo.surface_from_file(ojoin(TMPD, "all--hc1e_oilthickness--19991201.gri"))
    logger.info(x1e.values.mean())
    assert x1e.values.mean() == pytest.approx(0.516, abs=0.001)


def test_hc_thickness1f():
    """HC thickness with YAML config 1f; use rotated template map"""
    os.chdir(str(Path(__file__).absolute().parent.parent))
    xx.main(["--config", "tests/yaml/hc_thickness1f.yml"])

    x1f = xtgeo.surface_from_file(ojoin(TMPD, "all--hc1f_oilthickness--19991201.gri"))
    logger.info(x1f.values.mean())
    # other mean as the map is smaller; checked in RMS
    assert x1f.values.mean() == pytest.approx(1.0999, abs=0.0001)


def test_hc_thickness1g():
    """HC thickness with YAML config 1g; use rotated template map and both
    oil and gas"""
    os.chdir(str(Path(__file__).absolute().parent.parent))
    xx.main(["--config", "tests/yaml/hc_thickness1g.yml"])

    x1g1 = xtgeo.surface_from_file(ojoin(TMPD, "all--hc1g_oilthickness--19991201.gri"))
    logger.info(x1g1.values.mean())
    assert x1g1.values.mean() == pytest.approx(1.0999, abs=0.0001)

    x1g2 = xtgeo.surface_from_file(ojoin(TMPD, "all--hc1g_gasthickness--19991201.gri"))
    logger.info(x1g1.values.mean())
    assert x1g2.values.mean() == pytest.approx(0.000, abs=0.0001)


def test_hc_thickness1h():
    """Test HC thickness with YAML copy from 1a, with tuning to speed up"""
    os.chdir(str(Path(__file__).absolute().parent.parent))
    xx.main(["--config", "tests/yaml/hc_thickness1h.yml"])

    allz = xtgeo.surface_from_file(
        ojoin(TMPD, "all--tuning_oilthickness--20010101_19991201.gri")
    )
    val = allz.values1d

    print(np.nanmean(val), np.nanstd(val))

    # -0.0574 in RMS volumetrics, but within range as different approach
    assert np.nanmean(val) == pytest.approx(-0.0336, abs=0.005)
    assert np.nanstd(val) == pytest.approx(0.1717, abs=0.005)


def test_hc_thickness1i():
    """Test HC thickness with YAML config example 1i, based on 1a"""
    os.chdir(str(Path(__file__).absolute().parent.parent))
    xx.main(["--config", "tests/yaml/hc_thickness1i.yml"])

    allz = xtgeo.surface_from_file(
        ojoin(TMPD, "all--hc1i_oilthickness--20010101_19991201.gri")
    )
    val = allz.values

    print(val.mean())

    # -0.0574 in RMS volumetrics, but within range as different approach
    assert val.mean() == pytest.approx(-0.06, abs=0.01)
