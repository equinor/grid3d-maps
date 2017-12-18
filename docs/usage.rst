============
Usage
============

These are two command line scripts; one generates HC thickness maps, the
other makes average maps

::

   grid3d_hc_thickness --config myfile_hc.yaml

   grid3d_average_map --config myfile_avg.yaml


-------------------------
Override the Eclipse root
-------------------------

For both scripts, some settings in the YAML file can be overridden by
the command line, which can be useful in ERT setups::

   grid3d_hc_thickness --config myfile.yaml --eclroot GULLFAKS

-----------------------------
Possible command line options
-----------------------------

Type::

  grid3d_hc_thickness --help

  grid3d_average_map --help

--------------------------------------------
Example of YAML setup files for HC thickness
--------------------------------------------

HC thickness 1a
"""""""""""""""

.. literalinclude:: ../tests/yaml/hc_thickness1a.yaml
   :language: yaml

HC thickness 1b
"""""""""""""""

Another example where zonation is in a separate file, and faults are included
in the plots:

.. literalinclude:: ../tests/yaml/hc_thickness1b.yaml
   :language: yaml

The zonation file:

.. literalinclude:: ../tests/yaml/hc_thickness1b_zonation.yaml
   :language: yaml

Plots (examples):

Zone 1+3 oilthickness in 19991201:

.. image:: test_images/z1+3--hc1b_oilthickness--19991201.png

Difference oil column in Zone3:

.. image:: test_images/z3--hc1b_oilthickness--20010801_19991201.png

HC thickness 1c
"""""""""""""""

Example with automatic map settings:

.. literalinclude:: ../tests/yaml/hc_thickness1c.yaml
   :language: yaml


HC thickness 1d
"""""""""""""""

Example with Eclipse PORV is used as basis, instead of BULK*PORO*NTG (as
PORV may have been edited in the EDIT section):

.. literalinclude:: ../tests/yaml/hc_thickness1d.yaml
   :language: yaml

HC thickness 1e
"""""""""""""""

Example where the GRID input is a ROFF file, but the rest is from Eclipse
run:

.. literalinclude:: ../tests/yaml/hc_thickness1e.yaml
   :language: yaml

HC thickness 1f
"""""""""""""""

Example where a template map is given (can have rotation) in mapsettings

.. literalinclude:: ../tests/yaml/hc_thickness1f.yaml
   :language: yaml


----------------------------------
Example of setup for Average maps
----------------------------------

AVG example 1a
""""""""""""""

.. literalinclude:: ../tests/yaml/avg1a.yaml
   :language: yaml

With zonation file:

.. literalinclude:: ../tests/yaml/avg1a_zone.yaml
   :language: yaml


AVG example 1b
""""""""""""""

.. literalinclude:: ../tests/yaml/avg1b.yaml
   :language: yaml

.. image:: test_images/z1--avg1b_average_por.png

.. image:: test_images/z3--avg1b_average_por.png


AVG example 1c
""""""""""""""

With rotated map template and more plotsettings:

.. literalinclude:: ../tests/yaml/avg1c.yaml
   :language: yaml
