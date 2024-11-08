.. _allexamples:

============
Examples
============


---------------------------------------------
Examples of YAML setup files for HC thickness
---------------------------------------------

HC thickness 1a
"""""""""""""""

.. literalinclude:: ../tests/yaml/hc_thickness1a.yml
   :language: yaml

HC thickness 1b
"""""""""""""""

Another example where zonation is in a separate file, and faults are included
in the plots:

.. literalinclude:: ../tests/yaml/hc_thickness1b.yml
   :language: yaml

The zonation file:

.. literalinclude:: ../tests/yaml/hc_thickness1b_zonation.yml
   :language: yaml

Plots (examples):

All zones oilthickness in 19991201:

.. image:: test_to_docs/all--hc1b_oilthickness--19991201.png

Difference oil column:

.. image:: test_to_docs/all--hc1b_oilthickness--20010101_19991201.png

HC thickness 1c
"""""""""""""""

Example with automatic map settings:

.. literalinclude:: ../tests/yaml/hc_thickness1c.yml
   :language: yaml


HC thickness 1d
"""""""""""""""

Example with Eclipse PORV is used as basis, instead of BULK*PORO*NTG (as
PORV may have been edited in the EDIT section):

.. literalinclude:: ../tests/yaml/hc_thickness1d.yml
   :language: yaml

HC thickness 1e
"""""""""""""""

Example where the GRID input is a ROFF file, but the rest is from Eclipse
run:

.. literalinclude:: ../tests/yaml/hc_thickness1e.yml
   :language: yaml

HC thickness 1f
"""""""""""""""

Example where a template map is given (can have rotation) in mapsettings

.. literalinclude:: ../tests/yaml/hc_thickness1f.yml
   :language: yaml


HC thickness 1g
"""""""""""""""

Example as 1f, but with both phases (use mode comb or both)

.. literalinclude:: ../tests/yaml/hc_thickness1g.yml
   :language: yaml


HC thickness 1i
"""""""""""""""

Example as 1a, but use tuning to speed yp and truncate map with mask_outside
keyword (which will mask the map wher the sum of DZ is zero)

.. literalinclude:: ../tests/yaml/hc_thickness1i.yml
   :language: yaml


HC thickness 2a
"""""""""""""""

Use an RMS STOIIP (or similar) parameter instead of Eclipse stuff:

.. literalinclude:: ../tests/yaml/hc_thickness2a.yml
   :language: yaml


HC thickness 3a
"""""""""""""""

In this example two new features (from version 0.4) are demonstrated.
First is the option to use ``!include_from`` to load dates from the
``global_variables.yml``, and then the option to use property
filters is demonstrated.

Also for zones, ``!include`` can be used instead of the "yamlfile" approach
shown in example 1b.

The global_variables example (stub):

.. literalinclude:: ../tests/yaml/global_config3a.yml
   :language: yaml

The actual config:

.. literalinclude:: ../tests/yaml/hc_thickness3a.yml
   :language: yaml

HC thickness 3b
"""""""""""""""

As 3a, but no zonation entry. Zonation from filter

.. literalinclude:: ../tests/yaml/hc_thickness3b.yml
   :language: yaml


HC thickness 3c
"""""""""""""""

Base a zonation on a 3D grid property! Ie. that makes it possible
to make "irregular zonations", e.g. base it on a FIPNUM or EQLNUM
or whatever. Both Eclipse and ROFF input should be possible.

.. literalinclude:: ../tests/yaml/hc_thickness3c.yml
   :language: yaml

HC thickness 4a
"""""""""""""""

Find a pure rock thickness (no saturations involved). Can by useful for e.g.
a cumulative facies thickness when filter is activated, as in this example.

.. literalinclude:: ../tests/yaml/hc_thickness4a.yml
   :language: yaml

HC thickness hcdataio1a (dataio)
""""""""""""""""""""""""""""""""

Thickness maps (oil) using PORV from Eclipse files. Here fmu-dataio is the backend, for upload to
SUMO. See ``mapfolder`` is set to `magic` ``fmu-dataio``!

.. literalinclude:: ../docs/test_to_docs/hcdataio1a.yml
   :language: yaml

HC thickness hcdataio1b (dataio)
""""""""""""""""""""""""""""""""

Thickness maps for both gas and oil using PORV from Eclipse files and grid from roff. See
``mapfolder`` is set to `magic` ``fmu-dataio``! Alternatively ``mapfolder`` could just be missing.

.. literalinclude:: ../docs/test_to_docs/hcdataio1b.yml
   :language: yaml

HC thickness hcdataio1c (dataio)
""""""""""""""""""""""""""""""""

Thickness maps using STOIIP from roff files. Here fmu-dataio is the backend, for upload to
SUMO. This is default behaviour (from version 1.3) when ``mapfolder`` is missing

.. literalinclude:: ../docs/test_to_docs/hcdataio1c.yml
   :language: yaml


---------------------------------------
Examples of YAML setup for Average maps
---------------------------------------

AVG example 1a
""""""""""""""

.. literalinclude:: ../tests/yaml/avg1a.yml
   :language: yaml

With zonation file:

.. literalinclude:: ../tests/yaml/avg1a_zone.yml
   :language: yaml


AVG example 1b
""""""""""""""

.. literalinclude:: ../tests/yaml/avg1b.yml
   :language: yaml

.. image:: test_to_docs/z1--avg1b_average_por.png

.. image:: test_to_docs/z3--avg1b_average_por.png


AVG example 1c
""""""""""""""

With rotated map template and more plotsettings:

.. literalinclude:: ../tests/yaml/avg1c.yml
   :language: yaml


AVG example 1d
""""""""""""""

Map settings are omitted; they are estimated from grid:

.. literalinclude:: ../tests/yaml/avg1d.yml
   :language: yaml


AVG example 1e
""""""""""""""

Speed up computation with "tuning"

.. literalinclude:: ../tests/yaml/avg1e.yml
   :language: yaml


AVG example 2a
""""""""""""""

In this case, ``!include_from`` to read dates from a global master file is demonstrated,
as well the use of filters. A zone filter is replacing the "zonation" key

The global_variables example (stub):

.. literalinclude:: ../tests/yaml/global_config3a.yml
   :language: yaml

The configuration:

.. literalinclude:: ../tests/yaml/avg2a.yml
   :language: yaml


AVG example 2b
""""""""""""""

Base a zonation on a 3D grid property! Ie. that makes it possible
to make "irregular zonations", e.g. base it on a FIPNUM or EQLNUM
or whatever. Both Eclipse and ROFF input should be possible.

.. literalinclude:: ../tests/yaml/avg2b.yml
   :language: yaml

AVG example dataio 1a
"""""""""""""""""""""

Using FMU dataio as backend. Otherwise similar to previous case 2c. Note that a metadata section is
required for average data, and properties must occur under ``properties:``

.. literalinclude:: ../docs/test_to_docs/avgdataio1a.yml
   :language: yaml
