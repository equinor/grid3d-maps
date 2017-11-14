======================================
The scripts in *xtgeo_grid3d_map_apps*
======================================

Two scripts here, one for hc thickness maps and one for average maps.

* grid3d_hc_thickness

* grid3d_average_map


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


Credits
-------

The FMU team.
