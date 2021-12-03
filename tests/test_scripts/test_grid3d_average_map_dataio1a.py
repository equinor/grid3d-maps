"""Testing suite avg3, using dataio output."""
import os

import xtgeoapp_grd3dmaps.avghc.grid3d_average_map as grid3d_average_map

YAMLCONTENT = """
title: Reek
# Based on 2c, but use fmu-dataio as output

input:
  eclroot: tests/data/reek/REEK
  grid: $eclroot.EGRID

  # alternative approach to read a variables and dates:
  properties:
    - name: SWAT
      source: $eclroot.UNRST
      dates: !include_from tests/yaml/global_config3a.yml::global.DATES
      diffdates: !include_from tests/yaml/global_config3a.yml::global.DIFFDATES
      metadata:
        content: saturation
        unit: fraction
    - name: PRESSURE
      source: $eclroot.UNRST
      dates: !include_from tests/yaml/global_config3a.yml::global.DATES
      diffdates: !include_from tests/yaml/global_config3a.yml::global.DIFFDATES
      metadata:
        content: pressure
        unit: bar

zonation:
  zproperty:
    name: Zone
    source: tests/data/reek/reek_sim_zone.roff
    zones:
      - myzone1: [1] # refers to zonation numbers in 3D parameter
      - myzone2+3: [2, 3]

  #
  # zranges:
  #   - myzone1: [1, 5]  # refers to K layers

filters:
  - name: FACIES
    discrete: Yes
    source: tests/data/reek/reek_sim_facies2.roff
    discrange: [2] # Filter for a discrete will be spesic number sequence

computesettings:
  zone: Yes
  all: Yes
  mask_zeros: Yes # means that ouput maps will be set to undef where zero

# map definition (unrotated maps only, for rotated maps use a maptemplate...)
mapsettings:
  xori: 457000
  xinc: 50
  yori: 5927000
  yinc: 50
  ncol: 200
  nrow: 250

output:
  tag: avg2c # the tag will added to file name as extra info, e.g. as

  # Note: using the 'magical' fmu-dataio as argument!
  mapfolder: fmu-dataio
"""


def test_average_map3a(datatree):
    """Test AVG with YAML config example 3a piped through dataio"""

    cfg = datatree / "avg3a.yml"
    cfg.write_text(YAMLCONTENT)

    os.environ["FMU_GLOBAL_CONFIG"] = str(
        datatree / "tests" / "data" / "reek" / "global_variables.yml"
    )
    grid3d_average_map.main(["--config", "avg3a.yml", "--dump", "dump_config.yml"])
