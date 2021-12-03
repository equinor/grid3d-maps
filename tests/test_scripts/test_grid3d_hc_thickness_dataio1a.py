"""Testing suite avg3, using dataio output."""
import os

import xtgeoapp_grd3dmaps.avghc.grid3d_hc_thickness as grid3d_hc_thickness

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
  tag: hc1e
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
