============
Usage
============

These are two command line scripts; one generates HC thickness maps, the
other makes average maps

::

   grid3d_hc_thickness --config myfile_hc.yml

   grid3d_average_map --config myfile_avg.yml

-------------------------
Override the Eclipse root
-------------------------

For both scripts, some settings in the YAML file can be overridden by
the command line, which can be useful in ERT setups::

   grid3d_hc_thickness --config myfile.yml --eclroot GULLFAKS

-----------------------------
Possible command line options
-----------------------------

Type::

  grid3d_hc_thickness --help

  grid3d_average_map --help

-----------------------------
Tuning speed of the scripts
-----------------------------
In cases with large grids and many layers, computing can take a lot of time
as the internal griddata routine is not as fast as wished. The workaround
here is to use the tuning option in computesettings, e.g::

 computesettings:
   tuning:
     zone_avg: Yes
     coarsen: 3

Here, "zone_avg" means that a weighted average is done per zone, prior to the
2D mapping. Then, only the zone averages are gridded, which can speed up
the computing a lot.

Another option is "coarsen". If set to 3 as above, only every 3'rd grid cell
will be applied in the gridding.

Note however, that both options will inevitably reduce the *quality* of the
result, so there is a trade-off here. Se example :ref:`HC thickness 1i`.

------------------------------------------
Inactive map outside grid for HC thickness
------------------------------------------

With the average script, the resulting map will be inactive where the thickness
is zero. For the HC sum script, you need to active a setting in order to get
this:

.. code-block:: yaml

   computesettings:
     mask_outside: Yes


---------------------------------------
Using dates directly from global_config
---------------------------------------

From version 0.4 (experimental!)

For the thickness script, dates can now be loaded from the global_variables.yml
file, e.g. as:

.. code-block:: yaml

   input:
     eclroot: tests/data/reek/REEK
     dates: !include_from ../../share/fmuconfig/output/global_variables.yml::global.DATES
     diffdates: !include_from  ../../share/fmuconfig/output/global_variables.yml::global.DIFFDATES

Note that dates and diffdates are two separate lists


--------------------------------
Using fmu-dataio for SUMO output
--------------------------------

From version 1.3, a ``fmu-dataio`` pipeline is supported and encouraged. This will generate metadata
and make results compatible with upload to SUMO. This involves some changes:

  * The location of the FMU ``global_variables`` file must be set, which can be done either by:

    .. code-block:: yaml

        input:
          fmu_global_config: some_path/global_variables.yml  # relative to RUNPATH in ERT

    or by setting one of the following environment variables either in shell or inside ERT
    (see e.g. ``setenv`` in ERT)

    .. code-block:: bash

        # bash
        export FMU_GLOBAL_CONFIG_GRD3DMAPS=fmuconfig/output/global_variables.yml
        export FMU_GLOBAL_CONFIG=fmuconfig/output/global_variables.yml

    .. code-block:: csh

        # csh
        setenv FMU_GLOBAL_CONFIG_GRD3DMAPS fmuconfig/output/global_variables.yml
        setenv FMU_GLOBAL_CONFIG fmuconfig/output/global_variables.yml

    The first environment variable will be dedicated to the AVG and HC scripts, while the last one
    is a generic for ``fmu.dataio``. The priority is: first use the setting under ``input:`` in
    the script, then ``FMU_GLOBAL_CONFIG_GRD3DMAPS`` and finally ``FMU_GLOBAL_CONFIG``

  * The output.mapfolder must either:

    * be missing, as default now is fmu-dataio

    * be set to the magical string ``fmu-dataio``

  * For average maps, some additional metadata are needed, which shall be given in the
    ``metadata`` block under ``input.properties`` section, e.g.

  .. code-block:: yaml

      input:
        fmu_global_config: fmuconfig/output/global_variables.yml  # relative to RUNPATH in ERT
        eclroot: tests/data/reek/REEK
        grid: $eclroot.EGRID

        properties:
          - name: SWAT
            source: $eclroot.UNRST
            dates: !include_from tests/yaml/global_config3a.yml::global.DATES
            diffdates: !include_from tests/yaml/global_config3a.yml::global.DIFFDATES
            metadata:
              attribute: saturation
              unit: fraction

        ...

        output:
          mapfolder: fmu-dataio
