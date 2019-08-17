.. image:: https://travis-ci.com/equinor/xtgeoapp-grd3dmaps.svg?token=6jQHz1Rt4hEEy4skfFKt&branch=master
    :target: https://travis-ci.com/equinor/xtgeoapp-grd3dmaps
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

======================================
The scripts in *xtgeoapp_grd3dmaps*
======================================

Two scripts here, one for hc thickness maps and one for average maps.

Script grid3d_hc_thickness
--------------------------

Make Hydrocarbon thickness maps from Eclipse and/or Roff input

Script grid3d_average_map
-------------------------

Make average maps from a 3D grid parameter, Eclipse or Roff input

Features
--------

* From Eclipse files (EGRID, INIT, UNRST) and/or RMS binary ROFF
  make HCPV thickness maps, or make weighted average maps

  * No need to invoke RMS
  * Efficient in FMU work flows
  * HC thickness maps and average maps for property differences is
    supported (see examples in YAML config files)

* Outputs PNG figures and Irap (RMS) binary maps
* Simple configuration through a YAML file
* Configuration from YAML can be overriden by command line options
