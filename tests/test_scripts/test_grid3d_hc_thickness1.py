"Suite for HC thickness test set 1."

import shutil
from pathlib import Path

import numpy as np
import pytest
import xtgeo

import grid3d_maps.avghc.grid3d_hc_thickness as grid3d_hc_thickness

SOURCEPATH = Path(__file__).absolute().parent.parent.parent


def test_hc_thickness1a(datatree):
    """Test HC thickness with YAML config example 1a"""
    result = datatree / "hc1a_folder"
    result.mkdir(parents=True)
    dump = result / "hc1a_dump.yml"
    grid3d_hc_thickness.main(
        [
            "--config",
            "tests/yaml/hc_thickness1a.yml",
            "--dump",
            str(dump),
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )

    allz = xtgeo.surface_from_file(result / "all--oilthickness--20010101_19991201.gri")
    val = allz.values1d

    # -0.0574 in RMS volumetrics, but within range as different approach
    assert np.nanmean(val) == pytest.approx(-0.03653, 0.001)
    assert np.nanstd(val) == pytest.approx(0.199886, 0.001)


def test_hc_thickness1b_output_add2docs(datatree):
    """HC thickness with YAML config example 1b; zonation in own YAML file.

    Note that plots here goes into the Sphinx documentation!
    """
    result = datatree / "hc1b_folder"
    result.mkdir(parents=True)
    grid3d_hc_thickness.main(
        [
            "--config",
            "tests/yaml/hc_thickness1b.yml",
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )
    for img in result.glob("*hc1b*.png"):
        shutil.copy2(img, SOURCEPATH / "docs" / "test_to_docs")

    prp = xtgeo.surface_from_file(result / "all--hc1b_oilthickness--19991201.gri")
    assert prp.values.mean() == pytest.approx(0.82378, abs=0.001)


def test_hc_thickness1c(datatree):
    """HC thickness with YAML config example 1c; no map settings"""
    result = datatree / "hc1c_folder"
    result.mkdir(parents=True)
    grid3d_hc_thickness.main(
        [
            "--config",
            "tests/yaml/hc_thickness1c.yml",
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )

    prp = xtgeo.surface_from_file(result / "z1--hc1c_oilthickness--19991201.gri")
    assert prp.values.mean() == pytest.approx(0.27483, abs=0.001)

    x1d = xtgeo.surface_from_file(result / "all--hc1c_oilthickness--19991201.gri")
    assert x1d.values.mean() == pytest.approx(0.526, abs=0.001)


def test_hc_thickness1d(datatree):
    """HC thickness with YAML config example 1d; as 1c but use_porv instead"""
    result = datatree / "hc1d_folder"
    result.mkdir(parents=True)
    grid3d_hc_thickness.main(
        [
            "--config",
            "tests/yaml/hc_thickness1d.yml",
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )

    x1d = xtgeo.surface_from_file(result / "all--hc1d_oilthickness--19991201.gri")

    assert x1d.values.mean() == pytest.approx(0.516, abs=0.001)


def test_hc_thickness1e(datatree):
    """HC thickness with YAML config 1e; as 1d but use ROFF grid input"""
    result = datatree / "hc1e_folder"
    result.mkdir(parents=True)
    grid3d_hc_thickness.main(
        [
            "--config",
            "tests/yaml/hc_thickness1e.yml",
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )

    x1e = xtgeo.surface_from_file(result / "all--hc1e_oilthickness--19991201.gri")
    assert x1e.values.mean() == pytest.approx(0.516, abs=0.001)


def test_hc_thickness1f(datatree):
    """HC thickness with YAML config 1f; use rotated template map"""
    result = datatree / "hc1f_folder"
    result.mkdir(parents=True)

    grid3d_hc_thickness.main(
        [
            "--config",
            "tests/yaml/hc_thickness1f.yml",
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )

    x1f = xtgeo.surface_from_file(result / "all--hc1f_oilthickness--19991201.gri")
    # other mean as the map is smaller; checked in RMS
    assert x1f.values.mean() == pytest.approx(1.0999, abs=0.0001)


def test_hc_thickness1g(datatree):
    """HC thickness with YAML config 1g; use rotated template map and both
    oil and gas"""
    result = datatree / "hc1g_folder"
    result.mkdir(parents=True)

    grid3d_hc_thickness.main(
        [
            "--config",
            "tests/yaml/hc_thickness1g.yml",
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )

    x1g1 = xtgeo.surface_from_file(result / "all--hc1g_oilthickness--19991201.gri")
    assert x1g1.values.mean() == pytest.approx(1.0999, abs=0.0001)

    x1g2 = xtgeo.surface_from_file(result / "all--hc1g_gasthickness--19991201.gri")
    assert x1g2.values.mean() == pytest.approx(0.000, abs=0.0001)


def test_hc_thickness1h(datatree):
    """Test HC thickness with YAML copy from 1a, with tuning to speed up"""
    result = datatree / "hc1h_folder"
    result.mkdir(parents=True)

    grid3d_hc_thickness.main(
        [
            "--config",
            "tests/yaml/hc_thickness1h.yml",
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )

    allz = xtgeo.surface_from_file(
        result / "all--tuning_oilthickness--20010101_19991201.gri"
    )
    val = allz.values1d

    # -0.0574 in RMS volumetrics, but within range as different approach
    assert np.nanmean(val) == pytest.approx(-0.0336, abs=0.005)
    assert np.nanstd(val) == pytest.approx(0.1717, abs=0.005)


def test_hc_thickness1i(datatree):
    """Test HC thickness with YAML config example 1i, based on 1a"""
    result = datatree / "hc1i_folder"
    result.mkdir(parents=True)

    grid3d_hc_thickness.main(
        [
            "--config",
            "tests/yaml/hc_thickness1i.yml",
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )

    allz = xtgeo.surface_from_file(
        result / "all--hc1i_oilthickness--20010101_19991201.gri"
    )
    # -0.0574 in RMS volumetrics, but within range as different approach
    assert allz.values.mean() == pytest.approx(-0.06, abs=0.01)
