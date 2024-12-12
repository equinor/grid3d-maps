# grid3d-maps

[![tests](https://github.com/equinor/grid3d-maps/actions/workflows/test.yml/badge.svg)](https://github.com/equinor/grid3d-maps/actions/workflows/test.yml)
![Python Version](https://img.shields.io/badge/python-3.9%20|%203.10%20|%203.11-blue.svg)
[![License: GPL v3](https://img.shields.io/github/license/equinor/grid3d-maps)](https://www.gnu.org/licenses/gpl-3.0)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Various scripts for generating maps from 3D grid properties.

## Scripts included

| Script                  |     Description     |
|-------------------------|---------------------|
| `grid3d_hc_thickness`   | Make Hydrocarbon thickness maps from Eclipse and/or Roff input |
| `grid3d_average_map`    | Make average maps from a 3D grid parameter, Eclipse or Roff input |


## Features

- From Eclipse files (EGRID, INIT, UNRST) and/or RMS binary ROFF
  make HCPV thickness maps, or make weighted average maps
  - No need to invoke RMS
  - Efficient in FMU work flows
  - HC thickness maps and average maps for property differences is
    supported (see examples in YAML config files)
- Outputs PNG figures and Irap (RMS) binary maps
- Simple configuration through a YAML file
- Configuration from YAML can be overriden by command line options
- From version 1.3, output via `fmu-dataio`_ (to `sumo`_) is supported.
  See [fmu-dataio](https://github.com/equinor/fmu-dataio/) and
  [fmu-sumo](https://github.com/equinor/fmu-sumo)
