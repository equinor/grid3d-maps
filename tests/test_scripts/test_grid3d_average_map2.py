"""Testing suite avg2."""

import numpy.testing as nptest
import pytest
import xtgeo

import grid3d_maps.avghc.grid3d_average_map as grid3d_average_map

# =============================================================================
# Do tests
# =============================================================================


def test_average_map2a(datatree):
    """Test AVG with YAML config example 2a ECL based with filters"""
    result = datatree / "map2a_folder"
    result.mkdir(parents=True)
    dump = result / "avg2a.yml"
    grid3d_average_map.main(
        [
            "--config",
            "tests/yaml/avg2a.yml",
            "--dump",
            str(dump),
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )
    mymap = xtgeo.surface_from_file(
        result / "zone2+3--avg2a_average_swat--20010101_19991201.gri"
    )
    assert mymap.values.mean() == pytest.approx(0.0608, abs=0.001)


def test_average_map2b(datatree):
    """Test AVG with YAML config example 2b, filters, zonation from prop"""
    result = datatree / "map2b_folder"
    result.mkdir(parents=True)
    dump = result / "avg2b.yml"
    grid3d_average_map.main(
        [
            "--config",
            "tests/yaml/avg2b.yml",
            "--dump",
            str(dump),
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )

    pfile = result / "myzone1--avg2b_average_pressure--20010101.gri"
    pres = xtgeo.surface_from_file(pfile)

    assert pres.values.mean() == pytest.approx(301.6917, abs=0.01)

    # test dumped YAML file to reproduce result
    result2 = datatree / "map2b_folder_rerun"
    result2.mkdir(parents=True)
    grid3d_average_map.main(
        [
            "--config",
            str(result / "avg2b.yml"),
            "--mapfolder",
            str(result2),
            "--plotfolder",
            str(result2),
        ]
    )
    pfile = result2 / "myzone1--avg2b_average_pressure--20010101.gri"
    pres_rerun = xtgeo.surface_from_file(pfile)
    nptest.assert_array_equal(pres.values, pres_rerun.values)


def test_average_map2c(datatree):
    """Test AVG with YAML config example 2c, filters, zonation from prop"""
    result = datatree / "map2c_folder"
    result.mkdir(parents=True)
    dump = result / "avg2c.yml"
    grid3d_average_map.main(
        [
            "--config",
            "tests/yaml/avg2c.yml",
            "--dump",
            str(dump),
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )

    pfile = result / "myzone1--avg2c_average_pressure--20010101.gri"
    pres = xtgeo.surface_from_file(pfile)

    assert pres.values.mean() == pytest.approx(301.689869, abs=0.01)
