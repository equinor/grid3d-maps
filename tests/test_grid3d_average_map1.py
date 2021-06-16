import os
import sys
import shutil
import glob
from pathlib import Path

import pytest

import xtgeo
from xtgeo.common import XTGeoDialog

import xtgeoapp_grd3dmaps.avghc.grid3d_average_map as xx

xtg = XTGeoDialog()
logger = xtg.basiclogger(__name__)

if not xtg.testsetup():
    sys.exit(-9)

TMPD = xtg.tmpdir
testpath = xtg.testpath

skiplargetest = pytest.mark.skipif(xtg.bigtest is False, reason="Big tests skip")

# =============================================================================
# Do tests
# =============================================================================


def test_average_map1a():
    """Test HC thickness with YAML config example 1a ECL based"""
    os.chdir(str(Path(__file__).absolute().parent.parent))
    xx.main(["--config", "tests/yaml/avg1a.yml"])


def test_average_map1b():
    """Test HC thickness with YAML config example 1b ROFF based"""
    os.chdir(str(Path(__file__).absolute().parent.parent))
    xx.main(["--config", "tests/yaml/avg1b.yml"])

    z1poro = xtgeo.surface_from_file(os.path.join(TMPD, "z1--avg1b_average_por.gri"))
    assert z1poro.values.mean() == pytest.approx(0.1598, abs=0.001)
    assert z1poro.values.std() == pytest.approx(0.04, abs=0.003)

    imgs = glob.glob(os.path.join(TMPD, "*avg1b*.png"))
    for img in imgs:
        shutil.copy2(img, "docs/test_images/.")


def test_average_map1c():
    """Test HC thickness with YAML config example 1c ROFF based, rotated map"""
    os.chdir(str(Path(__file__).absolute().parent.parent))
    xx.main(["--config", "tests/yaml/avg1c.yml"])

    z1poro = xtgeo.surface_from_file(os.path.join(TMPD, "all--avg1c_average_por.gri"))
    assert z1poro.values.mean() == pytest.approx(0.1678, abs=0.001)


def test_average_map1d():
    """Test HC thickness with YAML config example 1d ROFF based, rotated map"""
    os.chdir(str(Path(__file__).absolute().parent.parent))
    xx.main(["--config", "tests/yaml/avg1d.yml"])


def test_average_map1e():
    """Test HC thickness with YAML config example 1e ROFF based, tuning"""
    os.chdir(str(Path(__file__).absolute().parent.parent))
    xx.main(["--config", "tests/yaml/avg1e.yml"])


def test_average_map1f():
    """Test HC thickness with YAML config example 1f ROFF based, zero layer"""
    os.chdir(str(Path(__file__).absolute().parent.parent))
    xx.main(["--config", "tests/yaml/avg1f.yml"])
