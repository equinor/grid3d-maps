=====
Usage
=====

xtgeo_grid3d_map_apps is a command line script that computes HC thicknesses
based on Eclipse input.


-------------------------
Running from command line
-------------------------

Minimum command line
^^^^^^^^^^^^^^^^^^^^

::

 xtgeo_grid3d_map_apps --config myfile.yaml

Override the Eclipse root
^^^^^^^^^^^^^^^^^^^^^^^^^

Her the Eclipse root in the YAML file is overriden at the command line,
which can be useful in ERT setups::

 xtgeo_grid3d_map_apps --config myfile.yaml --root GULLFAKS

Possible command line options
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Type::

  xtgeo_grid3d_map_apps --help

---------------------
Example of YAML setup
---------------------

Preferred setup
^^^^^^^^^^^^^^^

.. literalinclude:: ../tests/yaml/002.yaml
   :language: yaml

The zonation file:

.. literalinclude:: ../tests/yaml/002_x.yaml
   :language: yaml


Output plots (examples)
^^^^^^^^^^^^^^^^^^^^^^^

.. image:: test_images/tarbert--oilthickness--1985_10_01.png

.. image:: test_images/tarbert--oilthickness--2000_07_01.png

Difference map:

.. image:: test_images/tarbert--oilthickness--2000_07_01-1985_10_01.png

Old setup
^^^^^^^^^

The old YAML setup is still possible to use, but discouraged.

.. literalinclude:: ../tests/yaml/001.yaml
   :language: yaml
