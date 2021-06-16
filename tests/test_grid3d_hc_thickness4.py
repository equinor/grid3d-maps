import os
from pathlib import Path
import pytest

import xtgeo
from xtgeo.common import XTGeoDialog


import xtgeoapp_grd3dmaps.avghc.grid3d_hc_thickness as xxx

xtg = XTGeoDialog()

xtg = XTGeoDialog()
logger = xtg.basiclogger(__name__)

if not xtg.testsetup():
    raise SystemExit

TMPD = xtg.tmpdir
testpath = xtg.testpath


def test_hc_thickness4a():
    """HC thickness with external configfiles, HC 4a"""
    os.chdir(str(Path(__file__).absolute().parent.parent))
    dump = os.path.join(TMPD, "hc4a.yml")
    xxx.main(["--config", "tests/yaml/hc_thickness4a.yml", "--dump", dump])

    # check result
    mapfile = os.path.join(TMPD, "all--hc4a_rockthickness.gri")
    mymap = xtgeo.surface_from_file(mapfile)

    assert mymap.values.mean() == pytest.approx(0.76590, abs=0.001)
