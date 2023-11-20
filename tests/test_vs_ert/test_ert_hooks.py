"""Suite for testing through ERT."""
import subprocess
from pathlib import Path

import pytest
import yaml

XTGEOTESTDATA = "tests/data/reek"


@pytest.mark.requires_ert
def test_grid3d_maps_through_ert(datatree):
    """Test through ERT."""
    print(f"ERT run on {datatree}")

    eclbase = "REEK"

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

    # Configuration file for grid3d_thickness,
    # based on tests/yaml/avg1f.yml
    eclroot = str(Path(XTGEOTESTDATA) / "REEK")
    # (eclroot cannot be only in yaml, it is overriden by the forward model
    # default argument)
    hc_conf = {
        "title": "Reek",
        "input": {
            "grid": str(Path(XTGEOTESTDATA) / "reek_grid_fromegrid.roff"),
            "dates": ["19991201"],
        },
        "output": {"tag": "hc1f", "mapfolder": ".", "plotfolder": "."},
    }
    Path("hc_conf.yml").write_text(yaml.dump(hc_conf), encoding="utf8")

    ert_config = [
        "ECLBASE " + eclbase + ".DATA",
        "QUEUE_SYSTEM LOCAL",
        "NUM_REALIZATIONS 1",
        "RUNPATH .",
    ]

    ert_config.append("FORWARD_MODEL GRID3D_AVERAGE_MAP(<CONFIG_AVGMAP>=avg_conf.yml)")
    ert_config.append(
        "FORWARD_MODEL GRID3D_HC_THICKNESS(<CONFIG_HCMAP>=hc_conf.yml, <ECLROOT>="
        + eclroot
        + ")"
    )

    ert_config_filename = Path(datatree) / "grid3d_maps_test.ert"
    ert_config_filename.write_text("\n".join(ert_config))

    subprocess.call(["ert", "test_run", ert_config_filename])

    assert Path("zero--avg1f_average_dz.gri").is_file()
    assert Path("all--hc1f_oilthickness--19991201.png").is_file()
    assert Path("OK").is_file()
