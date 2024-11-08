.. highlight:: shell

============
Installation
============


Stable release
--------------

The stable release is on /project/res, so scripts can be run as:

.. code-block:: console

    $ grid3d_hc_thickness <options>
    $ grid3d_average_map <options>


From sources
------------

The sources for grid3d_maps can be downloaded from
the `equinor Git repo`_.

You can then clone the repository:

.. code-block:: console

    $ git clone git@github.com:equinor/grid3d-maps

Once you have a copy of the source, and you have a `virtual environment`_,
you can install locally (for development and testing) it with:

.. code-block:: console

    $ pip install -e .

However, if you will like to contribute, making a personal fork is strongly
recommended, see :ref:`Contributing`.

.. _equinor Git repo: https://github.com/equinor/grid3d-maps
.. _virtual environment: http://docs.python-guide.org/en/latest/dev/virtualenvs/
