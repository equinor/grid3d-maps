import shutil
from pathlib import Path

import pytest
import xtgeo

from xtgeoapp_grd3dmaps.aggregate import grid3d_aggregate_map


def _copy2docs(file):
    root = Path(__file__).absolute().parent.parent.parent
    dst = root / "docs" / "test_to_docs"
    shutil.copy2(file, dst)


def test_aggregated_map1_add2docs(datatree):
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
    swat = xtgeo.surface_from_file(result / "all--max_SWAT--20030101.gri")
    assert swat.values.min() == pytest.approx(0.14292679727077484, abs=1e-8)
    _copy2docs(cfg)


def test_aggregated_map2_add2docs(datatree):
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
    swat = xtgeo.surface_from_file(result / "all--min_SWAT--20030101.gri")
    assert swat.values.mean() == pytest.approx(0.7908786104444353, abs=1e-8)
    _copy2docs(cfg)


def test_aggregated_map3_add2docs(datatree):
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
    poro = xtgeo.surface_from_file(result / "all--mean_PORO.gri")
    assert poro.values.mean() == pytest.approx(0.1677586422488292, abs=1e-8)
    _copy2docs(cfg)


def test_aggregated_map4_add2docs(datatree):
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
    swat = xtgeo.surface_from_file(result / "zone1--max_SWAT--20030101.gri")
    assert swat.values.max() == pytest.approx(1.0000962018966675, abs=1e-8)
    assert (result / "all--max_SWAT--20030101.gri").is_file()
    assert (result / "zone2--max_SWAT--20030101.gri").is_file()
    assert (result / "zone3--max_SWAT--20030101.gri").is_file()
    _copy2docs(yml)


def test_aggregated_map5_add2docs(datatree):
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
    poro = xtgeo.surface_from_file(result / "all--mean_PORO.gri")
    assert poro.values.mean() == pytest.approx(0.1648792893163274, abs=1e-8)
    _copy2docs(cfg)


def test_aggregated_map6_add2docs(datatree):
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
    assert sorted(gri_files) == sorted([
        "all--max_SWAT--19991201",
        "all--max_SWAT--20030101",
        "FirstZone--max_SWAT--19991201",
        "FirstZone--max_SWAT--20030101",
        "SecondZone--max_SWAT--19991201",
        "SecondZone--max_SWAT--20030101",
        "ThirdZone--max_SWAT--19991201",
        "ThirdZone--max_SWAT--20030101",
    ])
    _copy2docs(cfg)
