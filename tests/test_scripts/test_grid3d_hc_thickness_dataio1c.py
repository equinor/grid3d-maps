"""Testing suite hc, using dataio output, which also is included in doc examples."""
import json
import os
import shutil
from pathlib import Path

import pytest
import xtgeo
import xtgeoapp_grd3dmaps.avghc.grid3d_hc_thickness as grid3d_hc_thickness
import yaml

YAMLCONTENT = """
title: Reek
# Use a STOIIP or HCPV property from RMS

input:
  grid: tests/data/reek/reek_geo_grid.roff
  # the name is the actual name of the parameter in the ROFF file
  # here STOIIP (if you don't know, try with 'null' as name to get first found!)
  stoiip: { null: tests/data/reek/reek_geo_stooip.roff }

  # date will just be informative (on plots etc) in this case
  dates: [19900101]

zonation:
  zranges:
    - Z1: [1, 5]
    - Z2: [6, 10]
    - Z3: [11, 14]

computesettings:
  mode: oil
  zone: Yes
  all: Yes
  # speed up:
  tuning:
    zone_avg: Yes
    coarsen: 2

# non-existing mapfolder will default to fmu-dataio!
output:
  tag: stoiip
"""

SOURCEPATH = Path(__file__).absolute().parent.parent.parent


def test_hc_thickness_1c_add2docs(datatree):
    """Test HC thickness map piped through dataio, see former yaml hc_thickness2a."""

    cfg = datatree / "hcdataio1c.yml"
    cfg.write_text(YAMLCONTENT)

    os.environ["FMU_GLOBAL_CONFIG"] = str(
        datatree / "tests" / "data" / "reek" / "global_variables.yml"
    )
    grid3d_hc_thickness.main(
        ["--config", "hcdataio1c.yml", "--dump", "dump_config.yml"]
    )

    # read result file
    res = datatree / "share" / "results" / "maps"
    surf = xtgeo.surface_from_file(res / "all--stoiip_oilthickness--19900101.gri")
    assert surf.values.mean() == pytest.approx(0.25476, rel=0.01)

    # read metadatafile
    with open(
        res / ".all--stoiip_oilthickness--19900101.gri.yml", encoding="utf8"
    ) as stream:
        metadata = yaml.safe_load(stream)

    if "DUMP" in os.environ:
        print(json.dumps(metadata, indent=4))

    assert metadata["data"]["spec"]["ncol"] == 292
    assert metadata["data"]["time"]["t0"]["value"] == "1990-01-01T00:00:00"

    # for auto documentation
    shutil.copy2(cfg, SOURCEPATH / "docs" / "test_to_docs")
