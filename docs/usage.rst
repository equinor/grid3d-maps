=====
Usage
=====

These are two command line scripts; one generates HC thickness maps, the
other makes average maps

::

   grid3d_hc_thickness --config myfile_hc.yaml

   grid3d_average_map --config myfile_avg.yaml


Override the Eclipse root
^^^^^^^^^^^^^^^^^^^^^^^^^

For both scripts, some settings in the YAML file can be overrdien at
the command line, which can be useful in ERT setups::

   grid3d_hc_thickness --config myfile.yaml --eclroot GULLFAKS

Possible command line options
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Type::

  xtgeo_grid3d_map_apps --help

---------------------------
Example of YAML setup files
---------------------------

HC thickness
^^^^^^^^^^^^

.. literalinclude:: ../tests/yaml/hc_thickness1.yaml
   :language: yaml

Another example where zonation is in a separate file:

.. literalinclude:: ../tests/yaml/hc_thickness2.yaml
   :language: yaml

The zonation file:

.. literalinclude:: ../tests/yaml/hc_thickness2_zonation.yaml
   :language: yaml

Example with automatic map settings:

.. literalinclude:: ../tests/yaml/hc_thickness3.yaml
   :language: yaml


Average maps
^^^^^^^^^^^^

.. literalinclude:: ../tests/yaml/avg1.yaml
   :language: yaml

With zonation file:

.. literalinclude:: ../tests/yaml/avg1_zone.yaml
   :language: yaml



Output plots (examples)
^^^^^^^^^^^^^^^^^^^^^^^

Later...
