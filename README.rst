=============================
The script *xtgeo_grid3d_map_apps*
=============================


Make HC thickness maps directly from Eclipse runs using XTGeo Python
library.



Features
--------

* From Eclipse files (EGRID, INIT, UNRST) make HCPV thickness maps

  * No need to invoke RMS
  * Efficient in FMU work flows

* Outputs PNG figures and Irap binary maps
* Configuration through a YAML file
* Configuration from YAML can be overriden by command line options

Example of a YAML input file:

.. literalinclude:: ../tests/yaml/004.yaml
   :language: yaml


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.
