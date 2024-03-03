"""Test suite hc 4."""

import pytest
import xtgeo

import grid3d_maps.avghc.grid3d_hc_thickness as grid3d_hc_thickness


def test_hc_thickness4a(datatree):
    """HC thickness with external configfiles, HC 4a"""

    result = datatree / "hc4a_folder"
    result.mkdir(parents=True)
    grid3d_hc_thickness.main(
        [
            "--config",
            "tests/yaml/hc_thickness4a.yml",
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )
    # check result
    mymap = xtgeo.surface_from_file(result / "all--hc4a_rockthickness.gri")

    assert mymap.values.mean() == pytest.approx(0.76590, abs=0.001)
