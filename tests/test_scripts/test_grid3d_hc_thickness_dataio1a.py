"""Testing suite avg3, using dataio output."""

import json
import os
import shutil
import sys
from pathlib import Path

import pytest
import xtgeo
import yaml

import grid3d_maps.avghc.grid3d_hc_thickness as grid3d_hc_thickness

YAMLCONTENT = """
title: Reek
#
# Using PORV as method; this resembles YAML file 1e
input:
  eclroot: tests/data/reek/REEK
  grid: tests/data/reek/reek_grid_fromegrid.roff
  dates:
    - 19991201

# Zonation gives what zones to compute over, and typically is similar
# to the zonation in RMS. Note that it is possible to read the zonation
# from an extrernal YAML file, via:
#   yamlfile: 'name_of_file.yml'
zonation:
  # zranges will normally be the Zone parameter, defined as K range cells
  zranges:
    - Z1: [1, 5]
    - Z2: [6, 10]
    - Z3: [11, 14]

computesettings:
  # choose oil, gas or both
  mode: oil
  critmode: No
  shc_interval: [0.1, 1] # saturation interv
  method: use_porv
  zone: Yes
  all: Yes

# output on form ~ z1--hc1e_oilthickness--19991201.gri
output:
  tag: hcdataio1a
  mapfolder: fmu-dataio
"""
SOURCEPATH = Path(__file__).absolute().parent.parent.parent


@pytest.fixture()
def hcdataio1aconfig(datatree):
    """Fixture to make config."""
    name = "hcdataio1a.yml"
    cfg = datatree / name

    cfg.write_text(YAMLCONTENT)

    # for auto documentation
    shutil.copy2(cfg, SOURCEPATH / "docs" / "test_to_docs")
    return name


def test_hc_thickness_1a_add2docs(hcdataio1aconfig):
    """For using pytest -k add2docs to be ran prior to docs building."""
    print("Export config to docs folder")
    assert hcdataio1aconfig is not None


@pytest.mark.skipif(
    sys.platform == "win32", reason="dataio currently uses NamedTemporaryFile"
)
def test_hc_thickness_1a(datatree, hcdataio1aconfig):
    """Test HC thickness map piped through dataio"""

    os.environ["FMU_GLOBAL_CONFIG_GRD3DMAPS"] = str(
        datatree / "tests" / "data" / "reek" / "global_variables.yml"
    )
    grid3d_hc_thickness.main(
        ["--config", hcdataio1aconfig, "--dump", "dump_config.yml"]
    )

    # read result file
    res = datatree / "share" / "results" / "maps"
    surf = xtgeo.surface_from_file(res / "all--hcdataio1a_oilthickness--19991201.gri")
    assert surf.values.mean() == pytest.approx(0.51616, rel=0.01)

    # read metadatafile
    with open(
        res / ".all--hcdataio1a_oilthickness--19991201.gri.yml", encoding="utf8"
    ) as stream:
        metadata = yaml.safe_load(stream)

    if "DUMP" in os.environ:
        print(json.dumps(metadata, indent=4))

    assert metadata["data"]["spec"]["ncol"] == 146
