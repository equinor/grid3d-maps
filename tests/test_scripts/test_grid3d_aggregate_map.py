from pathlib import Path

import pytest
import xtgeo

from grid3d_maps.aggregate import grid3d_aggregate_map


def test_aggregated_map1(datatree):
    result = datatree / "aggregate1_folder"
    result.mkdir(parents=True)
    cfg = "tests/yaml/aggregate1.yml"

    grid3d_aggregate_map.main(
        [
            "--config",
            cfg,
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )
    swat = xtgeo.surface_from_file(result / "all--max_swat--20030101.gri")
    assert swat.values.min() == pytest.approx(0.14292679727077484, abs=1e-8)


def test_aggregated_map2(datatree):
    result = datatree / "aggregate2_folder"
    result.mkdir(parents=True)
    cfg = "tests/yaml/aggregate2.yml"

    grid3d_aggregate_map.main(
        [
            "--config",
            cfg,
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )
    swat = xtgeo.surface_from_file(result / "all--min_swat--20030101.gri")
    assert swat.values.mean() == pytest.approx(0.7908786104444353, abs=1e-8)


def test_aggregated_map3(datatree):
    result = datatree / "aggregate3_folder"
    result.mkdir(parents=True)
    cfg = "tests/yaml/aggregate3.yml"

    grid3d_aggregate_map.main(
        [
            "--config",
            cfg,
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )
    poro = xtgeo.surface_from_file(result / "all--mean_poro.gri")
    assert poro.values.mean() == pytest.approx(0.1677586422488292, abs=1e-8)


def test_aggregated_map4(datatree):
    result = datatree / "aggregate4_folder"
    result.mkdir(parents=True)
    yml = "tests/yaml/aggregate4.yml"

    grid3d_aggregate_map.main(
        [
            "--config",
            yml,
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )
    swat = xtgeo.surface_from_file(result / "zone1--max_swat--20030101.gri")
    assert swat.values.max() == pytest.approx(1.0000962018966675, abs=1e-8)
    assert (result / "all--max_swat--20030101.gri").is_file()
    assert (result / "zone2--max_swat--20030101.gri").is_file()
    assert (result / "zone3--max_swat--20030101.gri").is_file()


def test_aggregated_map5(datatree):
    result = datatree / "aggregate5_folder"
    result.mkdir(parents=True)
    cfg = "tests/yaml/aggregate5.yml"

    grid3d_aggregate_map.main(
        [
            "--config",
            cfg,
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )
    poro = xtgeo.surface_from_file(result / "all--mean_poro.gri")
    assert poro.values.mean() == pytest.approx(0.1648792893163274, abs=1e-8)


def test_aggregated_map6(datatree):
    result = datatree / "aggregate6_folder"
    result.mkdir(parents=True)
    cfg = "tests/yaml/aggregate6.yml"

    grid3d_aggregate_map.main(
        [
            "--config",
            cfg,
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )
    gri_files = [p.stem for p in Path(result).glob("*.gri")]
    assert sorted(gri_files) == sorted(
        [
            "all--max_swat--19991201",
            "all--max_swat--20030101",
            "firstzone--max_swat--19991201",
            "firstzone--max_swat--20030101",
            "secondzone--max_swat--19991201",
            "secondzone--max_swat--20030101",
            "thirdzone--max_swat--19991201",
            "thirdzone--max_swat--20030101",
        ]
    )
