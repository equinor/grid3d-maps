import os
import sys
import glob
import tempfile
from typing import Optional, List
import xtgeo

from xtgeoapp_grd3dmaps.aggregate import (
    grid3d_aggregate_map,
    _co2_mass,
    _config,
    _parser,
)
from xtgeoapp_grd3dmaps.aggregate._config import CO2MassSettings
from ecl.eclfile import EclFile
from ecl.grid import EclGrid

from ._co2_mass import _extract_source_data

PROPERTIES_TO_EXTRACT = ["RPORV", "PORV", "SGAS", "DGAS", "BGAS", "DWAT",
                         "BWAT", "AMFG", "YMFG", "XMF2", "YMF2"]


# Module variables for ERT hook implementation:
# DESCRIPTION = (
#     "Generate migration time property maps. Docs:\n"
#     + "https://fmu-docs.equinor.com/docs/xtgeoapp-grd3dmaps/"
# )
# CATEGORY = "modelling.reservoir"
# EXAMPLES = """
# .. code-block:: console
#
#   FORWARD_MODEL GRID3D_MIGRATION_TIME(<CONFIG_MIGTIME>=conf.yml, <ECLROOT>=<ECLBASE>)
# """


def calculate_mass_property(
    grid_file: Optional[str],
    co2_mass_settings: CO2MassSettings,
    dates: List[str],
):
    """
    Calculates a 3D CO2 mass property from the provided grid and grid property
    files
    """
    print("calculate_mass_property()")
    # prop_spec = [
    #     _config.Property(source=f, name=property_name)
    #     for f in glob.glob(properties_files, recursive=True)
    # ]
    # Property(source='../xtgeoapp-grd3dmaps-as/tests/data/reek/REEK.UNRST', name='SGAS', lower_threshold=None)
    # <class 'xtgeoapp_grd3dmaps.aggregate._config.Property'>
    # x = ["SGAS", "SWAT"]  # PROPERTIES_TO_EXTRACT
    # prop_spec = [_config.Property(source=co2_mass_settings.unrst_source, name=p) for p in x]
    # grid = None if grid_file is None else xtgeo.grid_from_file(grid_file)
    # properties = _parser.extract_properties(prop_spec, grid, dates)
    # for x in properties:
    #     print(x.name)
    # print(len(properties))

    print("Reading files.")
    grid = EclGrid(grid_file)
    print(grid)
    unrst = EclFile(co2_mass_settings.unrst_source)
    print(unrst)
    init = EclFile(co2_mass_settings.init_source)
    print(init)

    source_data = _extract_source_data(
        grid_file,
        co2_mass_settings.unrst_source,
        PROPERTIES_TO_EXTRACT,
        co2_mass_settings.init_source,
        None
    )
    print(source_data)

    # print("Start fetching properties.")
    # properties, dates = _fetch_properties(
    #     unrst,
    #     PROPERTIES_TO_EXTRACT
    # )

    # print([x for x in properties])
    # print(dates)

    print("END")
    exit()
    # co2_prop = _co2_mass.generate_co2_mass_property(properties)
    # return co2_prop


def main(arguments=None):
    """
    Calculates co2 mass as a property and aggregates it to a 2D map
    """
    if arguments is None:
        arguments = sys.argv[1:]
    config_ = _parser.process_arguments(arguments)
    if config_.input.properties:
        raise ValueError(
            "CO2 mass computation does not take a property as input"
        )
    if config_.co2_mass_settings is None:
        raise ValueError(
            "CO2 mass computation needs co2_mass_settings as input"
        )
    mass_prop = calculate_mass_property(
        config_.input.grid,
        config_.co2_mass_settings,
        config_.input.dates
    )
    # t_prop = calculate_migration_time_property(
    #     p_spec.source,
    #     p_spec.name,
    #     p_spec.lower_threshold,
    #     config_.input.grid,
    #     config_.input.dates,
    # )
    # migration_time_property_to_map(config_, t_prop)


if __name__ == '__main__':
    main()
