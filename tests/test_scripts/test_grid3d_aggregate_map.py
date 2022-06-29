import pytest
import xtgeo

from xtgeoapp_grd3dmaps.aggregate import grid3d_aggregate_map


def test_aggregated_map1(datatree):
    result = datatree / "aggregate1_folder"
    result.mkdir(parents=True)
    grid3d_aggregate_map.main(
        [
            "--config",
            "tests/yaml/aggregate1.yml",
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )
    swat = xtgeo.surface_from_file(result / "all--max_SWAT--20030101.gri")
    assert swat.values.min() == pytest.approx(0.14292679727077484, abs=1e-8)


def test_aggregated_map2(datatree):
    result = datatree / "aggregate2_folder"
    result.mkdir(parents=True)
    grid3d_aggregate_map.main(
        [
            "--config",
            "tests/yaml/aggregate2.yml",
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )
    swat = xtgeo.surface_from_file(result / "all--min_SWAT--20030101.gri")
    assert swat.values.mean() == pytest.approx(0.7908786104444353, abs=1e-8)


def test_aggregated_map3(datatree):
    result = datatree / "aggregate3_folder"
    result.mkdir(parents=True)
    grid3d_aggregate_map.main(
        [
            "--config",
            "tests/yaml/aggregate3.yml",
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )
    poro = xtgeo.surface_from_file(result / "all--mean_PORO.gri")
    assert poro.values.mean() == pytest.approx(0.1677586422488292, abs=1e-8)


def test_aggregated_map4(datatree):
    result = datatree / "aggregate4_folder"
    result.mkdir(parents=True)
    grid3d_aggregate_map.main(
        [
            "--config",
            "tests/yaml/aggregate4.yml",
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )
    swat = xtgeo.surface_from_file(result / "zone1--max_SWAT--20030101.gri")
    assert swat.values.max() == pytest.approx(1.0000962018966675, abs=1e-8)
    assert (result / "all--max_SWAT--20030101.gri").is_file()
    assert (result / "zone2--max_SWAT--20030101.gri").is_file()
    assert (result / "zone3--max_SWAT--20030101.gri").is_file()


def test_aggregated_map5(datatree):
    result = datatree / "aggregate5_folder"
    result.mkdir(parents=True)
    grid3d_aggregate_map.main(
        [
            "--config",
            "tests/yaml/aggregate5.yml",
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )
    poro = xtgeo.surface_from_file(result / "all--mean_PORO.gri")
    assert poro.values.mean() == pytest.approx(0.1648792893163274, abs=1e-8)
