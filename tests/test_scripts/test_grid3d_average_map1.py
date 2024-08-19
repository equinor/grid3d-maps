"""Testing suite average_map1."""

import shutil
from pathlib import Path

import pytest
import xtgeo

import grid3d_maps.avghc.grid3d_average_map as grid3d_hc_thickness

SOURCEPATH = Path(__file__).absolute().parent.parent.parent


def test_average_map1a(datatree):
    """Test HC thickness with YAML config example 1a ECL based"""
    result = datatree / "map1a_folder"
    result.mkdir(parents=True)
    grid3d_hc_thickness.main(
        [
            "--config",
            "tests/yaml/avg1a.yml",
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )

    z1poro = xtgeo.surface_from_file(result / "z1--avg1a_average_poro.gri")
    assert z1poro.values.mean() == pytest.approx(0.1598, abs=0.001)


def test_average_map1b_output_add2docs(datatree):
    """Test HC thickness with YAML config example 1b ROFF based.

    Note that plots here goes directly into the Sphinx documentation!
    """
    result = datatree / "map1b_folder"
    result.mkdir(parents=True)
    grid3d_hc_thickness.main(
        [
            "--config",
            "tests/yaml/avg1b.yml",
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )

    z1poro = xtgeo.surface_from_file(result / "z1--avg1b_average_por.gri")
    assert z1poro.values.mean() == pytest.approx(0.1598, abs=0.001)
    assert z1poro.values.std() == pytest.approx(0.04, abs=0.003)

    # for auto documentation
    for img in result.glob("*avg1b*.png"):
        shutil.copy2(img, SOURCEPATH / "docs" / "test_to_docs")


def test_average_map1c(datatree):
    """Test HC thickness with YAML config example 1c ROFF based, rotated map"""
    result = datatree / "map1c_folder"
    result.mkdir(parents=True)
    grid3d_hc_thickness.main(
        [
            "--config",
            "tests/yaml/avg1c.yml",
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )

    z1poro = xtgeo.surface_from_file(result / "all--avg1c_average_por.gri")
    assert z1poro.values.mean() == pytest.approx(0.1678, abs=0.001)


def test_average_map1d(datatree):
    """Test HC thickness with YAML config example 1d ROFF based, rotated map"""
    result = datatree / "map1d_folder"
    result.mkdir(parents=True)
    grid3d_hc_thickness.main(
        [
            "--config",
            "tests/yaml/avg1d.yml",
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )
    mymap = xtgeo.surface_from_file(result / "all--avg1d_average_diffsat.gri")
    assert mymap.values.mean() == pytest.approx(-0.8691, abs=0.001)


def test_average_map1e(datatree):
    """Test HC thickness with YAML config example 1e ROFF based, tuning"""
    result = datatree / "map1e_folder"
    result.mkdir(parents=True)
    grid3d_hc_thickness.main(
        [
            "--config",
            "tests/yaml/avg1e.yml",
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )
    mymap = xtgeo.surface_from_file(result / "all--avg1e_average_diffsat.gri")
    assert mymap.values.mean() == pytest.approx(-0.865748, abs=0.001)


def test_average_map1f(datatree):
    """Test HC thickness with YAML config example 1f ROFF based, zero layer"""
    result = datatree / "map1f_folder"
    result.mkdir(parents=True)
    grid3d_hc_thickness.main(
        [
            "--config",
            "tests/yaml/avg1f.yml",
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )
    mymap = xtgeo.surface_from_file(result / "lower--avg1f_average_dz.gri")
    assert mymap.values.mean() == pytest.approx(2.633, abs=0.005)
    mymap = xtgeo.surface_from_file(result / "zero--avg1f_average_dz.gri")
    assert mymap.values.mask.all()
