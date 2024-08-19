import numpy as np
import pytest
import xtgeo

import grid3d_maps.avghc.grid3d_hc_thickness as grid3d_hc_thickness


def test_hc_thickness2a(datatree):
    """HC thickness with YAML config example 2a; use STOOIP prop from RMS"""

    result = datatree / "hc2a_folder"
    result.mkdir(parents=True)
    grid3d_hc_thickness.main(
        [
            "--config",
            "tests/yaml/hc_thickness2a.yml",
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )

    # read in result and check statistical values
    allz = xtgeo.surface_from_file(result / "all--stoiip_oilthickness--19900101.gri")

    val = allz.values1d
    val[val <= 0] = np.nan

    # compared with data from RMS:
    assert np.nanmean(val) == pytest.approx(1.9521, abs=0.01)
    assert np.nanstd(val) == pytest.approx(1.2873, abs=0.01)
