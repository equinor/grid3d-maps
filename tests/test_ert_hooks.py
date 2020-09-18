import os
import sys
import subprocess
import yaml

import pytest

try:
    import ert_shared  # noqa
except ImportError:
    pytest.skip(
        "ERT is not installed, skipping hook implementation tests.",
        allow_module_level=True,
    )

TESTDIR = os.path.dirname(os.path.abspath(__file__))


@pytest.mark.skipif(sys.version_info < (3, 6), reason="requires python3.6 or higher")
def test_xtgeoapps_through_ert(tmpdir):
    tmpdir.chdir()

    eclbase = "REEK"

    ert_config = [
        "ECLBASE " + eclbase + ".DATA",
        "QUEUE_SYSTEM LOCAL",
        "NUM_REALIZATIONS 1",
        "RUNPATH .",
    ]

    # This is not a full test env of grid3d_* tools, just the
    # installation of the forward models, so we will provide a dummy
    # yaml input making them fail.
    conf = {"title": "Reek", "input": 0}
    with open("conf.yml", "w") as file_h:
        file_h.write(yaml.dump(conf))

    ert_config.append("FORWARD_MODEL GRID3D_AVERAGE_MAP(<CONFIG_HCMAP>=conf.yml)")
    ert_config.append("FORWARD_MODEL GRID3D_HC_THICKNESS(<CONFIG_HCMAP>=conf.yml)")

    ert_config_filename = "xtgeoapps_test.ert"
    with open(ert_config_filename, "w") as file_h:
        file_h.write("\n".join(ert_config))

    subprocess.call(["ert", "test_run", ert_config_filename])

    # ERT will only get here if the jobs exists and are configured. There
    # is no OK file since the jobs did fail.
    assert os.path.exists("EXIT")
