import subprocess
from pathlib import Path

import yaml


TESTDIR = Path(__file__).absolute().parent
XTGEOTESTDATA = TESTDIR.parent.parent / "xtgeo-testdata"

assert (
    XTGEOTESTDATA.is_dir()
), "Please clone xtgeo-testdata alongside this repo for test to run"


def test_xtgeoapps_through_ert(tmpdir):
    tmpdir.chdir()

    eclbase = "REEK"

    # Configuration file for grid3d_average_map,
    # based on tests/yaml/avg1f.yml
    avg_conf = {
        "title": "Reek",
        "input": {
            "folderroot": str(XTGEOTESTDATA / "3dgrids" / "reek"),
            "grid": "$folderroot/reek2_grid_w_zerolayer.roff",
            "dz": "$folderroot/reek2_grid_w_zerolayer_dz.roff",
        },
        "zonation": {"zranges": [{"ZERO": [15, 15]}]},
        "plotsettings": {
            "faultpolygons": str(
                XTGEOTESTDATA
                / "polygons"
                / "reek"
                / "1"
                / "top_upper_reek_faultpoly.xyz"
            ),
            "dz": {"valuerange": [0, 3]},
        },
        "computesettings": {
            "zone": True,
            "all": False,
            "tuning": {"zone_avg": True, "coarsen": 2},
        },
        "output": {"tag": "avg1f", "mapfolder": ".", "plotfolder": "."},
    }
    Path("avg_conf.yml").write_text(yaml.dump(avg_conf))

    # Configuration file for grid3d_thickness,
    # based on tests/yaml/avg1f.yml
    eclroot = str(XTGEOTESTDATA / "3dgrids" / "reek" / "REEK")
    # (eclroot cannot be only in yaml, it is overriden by the forward model
    # default argument)
    hc_conf = {
        "title": "Reek",
        "input": {
            "grid": str(
                XTGEOTESTDATA / "3dgrids" / "reek" / "reek_grid_fromegrid.roff"
            ),
            "dates": ["19991201"],
        },
        "output": {"tag": "hc1f", "mapfolder": ".", "plotfolder": "."},
    }
    Path("hc_conf.yml").write_text(yaml.dump(hc_conf))

    ert_config = [
        "ECLBASE " + eclbase + ".DATA",
        "QUEUE_SYSTEM LOCAL",
        "NUM_REALIZATIONS 1",
        "RUNPATH .",
    ]
    # Path("tmp").mkdir()

    ert_config.append("FORWARD_MODEL GRID3D_AVERAGE_MAP(<CONFIG_AVGMAP>=avg_conf.yml)")
    ert_config.append(
        "FORWARD_MODEL GRID3D_HC_THICKNESS(<CONFIG_HCMAP>=hc_conf.yml, <ECLROOT>="
        + eclroot
        + ")"
    )

    ert_config_filename = Path(tmpdir) / "xtgeoapps_test.ert"
    ert_config_filename.write_text("\n".join(ert_config))

    subprocess.call(["ert", "test_run", ert_config_filename])

    assert Path("zero--avg1f_average_dz.gri").is_file()
    assert Path("all--hc1f_oilthickness--19991201.png").is_file()
    assert Path("OK").is_file()
