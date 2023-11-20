import pytest
import xtgeo

import grid3d_maps.avghc.grid3d_hc_thickness as grid3d_hc_thickness


def test_hc_thickness3a(datatree):
    """HC thickness with external configfiles, HC 3a"""
    result = datatree / "hc3a_folder"
    result.mkdir(parents=True)
    dump = result / "hc3a_dump.yml"
    grid3d_hc_thickness.main(
        [
            "--config",
            "tests/yaml/hc_thickness3a.yml",
            "--dump",
            str(dump),
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )
    res = xtgeo.surface_from_file(result / "z2--hc3a_oilthickness--20010101.gri")
    assert res.values.max() == pytest.approx(5.8094, abs=0.001)  # qc'ed RMS


def test_hc_thickness3b(datatree):
    """HC thickness with external configfiles, HC 3b"""
    result = datatree / "hc3b_folder"
    result.mkdir(parents=True)
    dump = result / "hc3b_dump.yml"
    grid3d_hc_thickness.main(
        [
            "--config",
            "tests/yaml/hc_thickness3b.yml",
            "--dump",
            str(dump),
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )
    res = xtgeo.surface_from_file(result / "myzone1+3--hc3b_oilthickness--19991201.gri")
    assert res.values.max() == pytest.approx(6.3532, abs=0.001)  # qc'ed RMS


def test_hc_thickness3c(datatree):
    """HC thickness with external configfiles, HC 3c"""
    result = datatree / "hc3c_folder"
    result.mkdir(parents=True)
    grid3d_hc_thickness.main(
        [
            "--config",
            "tests/yaml/hc_thickness3c.yml",
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )

    res = xtgeo.surface_from_file(result / "myfip1--hc3c_oilthickness--19991201.gri")
    assert res.values.max() == pytest.approx(13.5681, abs=0.001)  # qc'ed RMS

    res = xtgeo.surface_from_file(result / "myfip2--hc3c_oilthickness--19991201.gri")
    assert res.values.max() == pytest.approx(0.0, abs=0.001)  # qc'ed RMS
