"""Testing suite hc, using dataio output."""
import os

import xtgeoapp_grd3dmaps.avghc.grid3d_hc_thickness as grid3d_hc_thickness

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
  mode: both
  critmode: No
  shc_interval: [0.1, 1] # saturation interv
  method: use_porv
  zone: Yes
  all: Yes

output:
  tag: hc1g
  mapfolder: fmu-dataio
"""


def test_hc_thickness_1a(datatree):
    """Test HC thickness map piped through dataio"""

    cfg = datatree / "hc1a.yml"
    cfg.write_text(YAMLCONTENT)

    os.environ["FMU_GLOBAL_CONFIG"] = str(
        datatree / "tests" / "data" / "reek" / "global_variables.yml"
    )
    grid3d_hc_thickness.main(["--config", "hc1a.yml", "--dump", "dump_config.yml"])
