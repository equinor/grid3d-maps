"""Testing suite hc, using dataio output."""

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

# Using PORV as method, and a rotated template map in mapsettings
# Reproduce hc_thickness1g.yml

input:
  eclroot: tests/data/reek/REEK
  grid: tests/data/reek/reek_grid_fromegrid.roff
  dates:
    - 19991201

zonation:
  zranges:
    - Z1: [1, 5]

mapsettings:
  templatefile: tests/data/reek/reek_hcmap_rotated.gri

computesettings:
  # choose oil, gas or both
  mode: both                                  # <<
  critmode: No
  shc_interval: [0.1, 1] # saturation interv
  method: use_porv
  zone: Yes
  all: Yes
  unit: m   # e.g. 'feet'; if missing, default is 'm' for metric

output:
  tag: hcdataio1b
  mapfolder: fmu-dataio

"""
SOURCEPATH = Path(__file__).absolute().parent.parent.parent


@pytest.fixture()
def hcdataio1bconfig(datatree):
    """Fixture to make config."""
    name = "hcdataio1b.yml"
    cfg = datatree / name

    cfg.write_text(YAMLCONTENT)

    # for auto documentation
    shutil.copy2(cfg, SOURCEPATH / "docs" / "test_to_docs")
    return name


def test_hc_thickness_1b_add2docs(hcdataio1bconfig):
    """For using pytest -k add2docs to be ran prior to docs building."""
    print("Export config to docs folder")
    assert hcdataio1bconfig is not None


@pytest.mark.skipif(
    sys.platform == "win32", reason="dataio currently uses NamedTemporaryFile"
)
def test_hc_thickness_1b(datatree, hcdataio1bconfig):
    """Test HC thickness map piped through dataio, using 'both' mode"""

    os.environ["FMU_GLOBAL_CONFIG_GRD3DMAPS"] = str(
        datatree / "tests" / "data" / "reek" / "global_variables.yml"
    )
    grid3d_hc_thickness.main(
        ["--config", hcdataio1bconfig, "--dump", "dump_config.yml"]
    )

    # read result file
    res = datatree / "share" / "results" / "maps"
    surf = xtgeo.surface_from_file(res / "all--hcdataio1b_oilthickness--19991201.gri")
    assert surf.values.mean() == pytest.approx(1.09999, rel=0.01)

    # read metadatafile
    with open(
        res / ".all--hcdataio1b_oilthickness--19991201.gri.yml", encoding="utf8"
    ) as stream:
        metadata = yaml.safe_load(stream)

    if "DUMP" in os.environ:
        print(json.dumps(metadata, indent=4))

    assert metadata["data"]["spec"]["ncol"] == 161
    assert metadata["data"]["content"] == "property"
