"""Suite for testing through ERT."""

import subprocess
from pathlib import Path

import pytest
import yaml

pytest.importorskip("ert")

XTGEOTESTDATA = "tests/data/reek"
ECLROOT = "tests/data/reek/REEK"

ERT_CONFIG = """
ECLBASE REEK.DATA
QUEUE_SYSTEM LOCAL
NUM_REALIZATIONS 1
RUNPATH .
"""


@pytest.mark.requires_ert
def test_average_map_no_eclroot(datatree):
    """Test avg maps through ERT using grid and prop from config."""
    print(f"ERT run on {datatree}")

    # Configuration file for grid3d_average_map,
    # based on tests/yaml/avg1f.yml
    avg_conf = {
        "title": "Reek",
        "input": {
            "folderroot": XTGEOTESTDATA,
            "grid": "$folderroot/reek2_grid_w_zerolayer.roff",
            "dz": "$folderroot/reek2_grid_w_zerolayer_dz.roff",
        },
        "zonation": {"zranges": [{"ZERO": [15, 15]}]},
        "plotsettings": {
            "faultpolygons": str(Path(XTGEOTESTDATA) / "top_upper_reek_faultpoly.xyz"),
            "dz": {"valuerange": [0, 3]},
        },
        "computesettings": {
            "zone": True,
            "all": False,
            "tuning": {"zone_avg": True, "coarsen": 2},
        },
        "output": {"tag": "avg1f", "mapfolder": ".", "plotfolder": "."},
    }
    Path("avg_conf.yml").write_text(yaml.dump(avg_conf), encoding="utf8")

    ert_config = Path(datatree) / "grid3d_maps_test.ert"
    ert_config.write_text(
        ERT_CONFIG + "FORWARD_MODEL GRID3D_AVERAGE_MAP(<CONFIG_AVGMAP>=avg_conf.yml)"
    )

    subprocess.call(["ert", "test_run", ert_config])

    assert Path("zero--avg1f_average_dz.gri").is_file()
    assert Path("OK").is_file()


@pytest.mark.requires_ert
def test_average_map_eclroot_in_config(datatree):
    """Test avg maps through ERT using eclroot in config."""
    print(f"ERT run on {datatree}")

    # eclroot defined in config
    avg_conf = {
        "title": "Reek",
        "input": {"eclroot": str(ECLROOT), "PORO": "$eclroot.INIT"},
        "computesettings": {"all": True, "tuning": {"zone_avg": True, "coarsen": 2}},
        "output": {"tag": "erttest", "mapfolder": "."},
    }
    Path("avg_conf.yml").write_text(yaml.dump(avg_conf), encoding="utf8")

    # eclroot not input as argument
    ert_config = Path(datatree) / "grid3d_maps_test.ert"
    ert_config.write_text(
        ERT_CONFIG + "FORWARD_MODEL GRID3D_AVERAGE_MAP(<CONFIG_AVGMAP>=avg_conf.yml)"
    )

    subprocess.call(["ert", "test_run", ert_config])

    assert Path("all--erttest_average_poro.gri").is_file()
    assert Path("OK").is_file()


@pytest.mark.requires_ert
def test_average_map_eclroot_in_forward_model(datatree):
    """Test avg maps through ERT using eclroot as forward_model argument."""
    print(f"ERT run on {datatree}")

    # eclroot not present in config
    avg_conf = {
        "title": "Reek",
        "input": {"PORO": "$eclroot.INIT"},
        "computesettings": {"all": True, "tuning": {"zone_avg": True, "coarsen": 2}},
        "output": {"tag": "erttest", "mapfolder": "."},
    }
    Path("avg_conf.yml").write_text(yaml.dump(avg_conf), encoding="utf8")

    # eclroot input as forward_model argument
    ert_config = Path(datatree) / "grid3d_maps_test.ert"
    ert_config.write_text(
        ERT_CONFIG + "FORWARD_MODEL GRID3D_AVERAGE_MAP(<CONFIG_AVGMAP>=avg_conf.yml, "
        f"<ECLROOT>={ECLROOT})"
    )

    subprocess.call(["ert", "test_run", ert_config])

    assert Path("all--erttest_average_poro.gri").is_file()
    assert Path("OK").is_file()


@pytest.mark.requires_ert
def test_hc_thickness_eclroot_in_forward_model(datatree):
    """Test hc-thickness through ERT using eclroot as forward_model argument."""
    print(f"ERT run on {datatree}")

    # eclroot not present in config
    hc_conf = {
        "title": "Reek",
        "input": {"dates": ["19991201"]},
        "output": {"tag": "hc1f", "mapfolder": ".", "plotfolder": "."},
    }
    Path("hc_conf.yml").write_text(yaml.dump(hc_conf), encoding="utf8")

    # eclroot input as forward_model argument
    ert_config = Path(datatree) / "grid3d_maps_test.ert"
    ert_config.write_text(
        ERT_CONFIG + "FORWARD_MODEL GRID3D_HC_THICKNESS(<CONFIG_HCMAP>=hc_conf.yml, "
        f"<ECLROOT>={ECLROOT})"
    )
    subprocess.call(["ert", "test_run", ert_config])

    assert Path("all--hc1f_oilthickness--19991201.png").is_file()
    assert Path("OK").is_file()


@pytest.mark.requires_ert
def test_hc_thickness_eclroot_in_config(datatree):
    """Test hc-thickness through ERT using eclroot in config."""
    print(f"ERT run on {datatree}")

    # eclroot defined in config
    hc_conf = {
        "title": "Reek",
        "input": {"eclroot": ECLROOT, "dates": ["19991201"]},
        "output": {"tag": "hc1f", "mapfolder": ".", "plotfolder": "."},
    }
    Path("hc_conf.yml").write_text(yaml.dump(hc_conf), encoding="utf8")

    # eclroot not input as argument
    ert_config = Path(datatree) / "grid3d_maps_test.ert"
    ert_config.write_text(
        ERT_CONFIG + "FORWARD_MODEL GRID3D_HC_THICKNESS(<CONFIG_HCMAP>=hc_conf.yml)"
    )

    subprocess.call(["ert", "test_run", ert_config])

    assert Path("all--hc1f_oilthickness--19991201.png").is_file()
    assert Path("OK").is_file()
