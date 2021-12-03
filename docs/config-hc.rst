Config file for HC thickness script
===================================

Options for HC thickness
------------------------

In the HC thickness settings there are some options that need explanation:

Method "use_poro"
^^^^^^^^^^^^^^^^^

Given Eclipse keywords, the HC thickness is based on
PORO, NTG, DZ, SHC, where SHC is SOIL or SGAS. The hydrocarbon
fraction (e.g. oil) is then multiplied with the cell thickness::

 HCPFDZ =  PORO * NTG * SOIL * DZ

Method "use_porv"
^^^^^^^^^^^^^^^^^

Uses the PORV instead::

 AREA = DX * DY
 HCPFDZ = PORV * SOIL / AREA

Method "dz_only"
^^^^^^^^^^^^^^^^^

This is a specal version, looking at BULK thickness, *not* NET thcikness. All
rock outside a specified saturation interval will a weight zero in the computation.


Overview of HC input file
-------------------------

The input file is a YAML based file, which shall have extension ``.yml``.

The format is mostly standard YAML, but a few extra directives ``!include`` and
``!include_from`` have been added.

The YAML file is indent based, where each main indent level is described below.

The ``title`` section
---------------------

This key is only the the name of the field or segment (optional).


The ``input`` section
---------------------

This section is required. It can have several variant, depending if Eclipse or ROFF
is input, or if a global config is used for dates.

Input from Eclipse using ECLIPSE root
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Note that .EGRID, .INIT, and .UNRST are the supported file formats for Eclipse.

The following example shows input from Eclipse where a Eclipse root name must exists.

.. code-block:: yaml

   input:
     eclroot: tests/data/reek/REEK
     dates:
       - 19991201
       - 20021101
       - 20021111
       - 20010101-19991201  # difference map


Input from Eclipse using alternative ROFF based grid
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is possible to use a grid spsfication from a ROFF file instead of an EGRID file:

.. code-block:: yaml

   input:
     eclroot: tests/data/reek/REEK
     grid: tests/data/reek/reek_grid_fromegrid.roff
     dates:
       - 19991201


Input from RMS ROFF files
^^^^^^^^^^^^^^^^^^^^^^^^^

Existing STOOIP or HCPV 3D parameters can be used instead. This makes it possible
to make HC thickness maps from geomodels directly.


.. code-block:: yaml

   input:
     grid: tests/data/reek/reek_geo_grid.roff
     stoiip: {STOIIP: tests/data/reek/reek_geo_stooip.roff}
     dates: [19900101]

The "STOIIP" in the example above is the name of the property within the ROFF file. If this name is
not known, try 'null' as name instead (also 'unknown' is supported for backward compatibility). The
date is purely informative.


Input Eclipse with dates from external config
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

New from version 0.4.

Dates can now be read directly from an external global-variables YAML file:

.. code-block:: yaml

   input:
     eclroot: tests/data/reek/REEK
     dates: !include_from tests/yaml/global_config3a.yml::global.DATES
     diffdates: !include_from tests/yaml/global_config3a.yml::global.DIFFDATES


The ``filter`` section
----------------------

This section is optional. The thickness map may be filtered on one or more
properties, either continuous of discrete. For example:

.. code-block:: yaml

   filters:
     -
       name: PORO
       source: $eclroot.INIT
       intvrange: [0.2, 1.0]  # Filter for a continuous will be an interval
     -
       name: FACIES
       discrete: Yes
       source: tests/data/reek/reek_sim_facies2.roff
       discrange: [1]  # Filter for a discrete will be spesic number (code)


The ``zonation`` section
------------------------

This section is optional (more text to come)


The ``mapsettings`` section
---------------------------

Text coming...


The ``computesettings`` section
-------------------------------

Text coming...


The ``output`` section
----------------------

A missing output will (from version 1.3):

* Output maps via `fmu-dataio <https://github.com/equinor/fmu-dataio/>`_.
* Output plots to ``/tmp`` folder

For other settings, see :ref:`allexamples`
