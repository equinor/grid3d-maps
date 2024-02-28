#!/usr/bin/env python
import os
import sys
import tempfile
import xtgeo
import yaml
from typing import List, Optional, Dict, Tuple
from xtgeoapp_grd3dmaps.aggregate import (
    _co2_mass,
    _config,
    _parser,
    grid3d_aggregate_map,
)
from xtgeoapp_grd3dmaps.aggregate._config import (CO2MassSettings,Zonation)
from ccs_scripts.co2_containment.co2_calculation import calculate_co2

PROPERTIES_TO_EXTRACT = [
    "RPORV",
    "PORV",
    "SGAS",
    "DGAS",
    "BGAS",
    "DWAT",
    "BWAT",
    "AMFG",
    "YMFG",
    "XMF2",
    "YMF2",
]


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


def generate_co2_mass_maps(config_) :

    """
    Calculates and exports 2D and 3D CO2 mass properties from the provided config file

    Args:
        config_: Arguments in the config file
    """

    co2_mass_settings = config_.co2_mass_settings
    zonation = config_.zonation
    zones = co2_mass_settings.zones
    if zones is not None and isinstance(zones, str):
        co2_mass_settings.zones = [zones]
    grid_file = config_.input.grid
    zone_info = {"source": None, "zranges": None}
    region_info = {"source": None, "property_name": None}
    co2_data = calculate_co2(
        grid_file=grid_file,
        unrst_file=co2_mass_settings.unrst_source,
        calc_type_input="mass",
        init_file=co2_mass_settings.init_source,
        zone_info=zone_info,
        region_info=region_info,
    )
    dates = config_.input.dates
    if len(dates)>0:
        co2_data.data_list = [x for x in co2_data.data_list if x.date in dates]
    out_property_list = _co2_mass.translate_co2data_to_property(
        co2_data,
        grid_file,
        co2_mass_settings,
        PROPERTIES_TO_EXTRACT,
        config_.output.mapfolder + "/grid",
    )
    config_.zonation.zranges, all_zrange = process_zonation(co2_mass_settings,grid_file,zonation)
    if len(config_.zonation.zranges)>0:
        config_.zonation.zproperty = None
    if config_.computesettings.all:
        config_.zonation.zranges.append({'all':all_zrange})
        config_.computesettings.all = False
        if not config_.computesettings.zone:
            config_.computesettings.zone = True
            config_.zonation.zranges = [zrange for zrange in config_.zonation.zranges if 'all' in zrange]
    co2_mass_property_to_map(config_,out_property_list)

def co2_mass_property_to_map(
    config_: _config.RootConfig,
    property_list: List[xtgeo.GridProperty],
):
    """
    Aggregates with SUM and writes a list of CO2 mass property to files
    using `grid3d_aggregate_map`.

    Args:
        config_: Arguments in the config file
        property_list: List of Grid property objects to be aggregated

    """
    config_.input.properties = []
    config_.computesettings.aggregation = _config.AggregationMethod.SUM
    config_.output.aggregation_tag = False
    for props in property_list:
        if len(props)>0 :
            for prop in props:
                config_.input.properties.append(_config.Property(config_.output.mapfolder+
                                                                 "/grid/"+prop.name+"--"+
                                                                 prop.date+".roff", None, None))
    grid3d_aggregate_map.generate_from_config(config_)

def process_zonation(co2_mass_settings: _config.CO2MassSettings,
                     grid_file: str,
                     zonation: Optional[_config.Zonation]=None
                     ) -> Tuple[List,List]:
    """
    Processes a zonation file, if existing, and extracts both zranges per zone
    and the complete range in the zaxis. Otherwise, uses the grid_file.

    Args:
        co2_mass_settings: Arguments in CO2 mass settings
        grid_file: Path to grid file
        zonation: Arguments in zonation

    Returns:
        Tuple[List,List]
    """
    if zonation.zproperty is not None or len(zonation.zranges)>0:
        if zonation.zproperty is not None:
            if zonation.zproperty.source.split(".")[-1] in ["yml", "yaml"]:
                zfile = read_yml_file(zonation.zproperty.source)
                zonation.zranges = zfile['zranges']
        if len(zonation.zranges) > 0:
            zone_names = [list(item.keys())[0] for item in zonation.zranges]
            zranges_limits = [list(d.values())[0] for d in zonation.zranges]
    else:
        grid_pf = xtgeo.grid_from_file(grid_file)
        zranges_limits = [[1,grid_pf.nlay]]
        zone_names = None
    max_zvalue = max(sublist[-1] for sublist in zranges_limits)
    min_zvalue = min(sublist[0] for sublist in zranges_limits)
    all_zrange = [min_zvalue, max_zvalue]
    if zone_names is not None:
        if co2_mass_settings.zones is not None:
            zones_to_plot = [zone for zone in co2_mass_settings.zones if zone in zone_names]
            if len(zones_to_plot) == 0:
                print(
                    "The zones specified in CO2 mass settings are not part of the zonation provided \n maps will be exported for all the existing zones")
                return zonation.zranges,all_zrange
            else:
                return [item for item in zonation.zranges if list(item.keys())[0] in zones_to_plot],all_zrange
        else:
            return zonation.zranges,all_zrange
    else:
        return [], all_zrange

def read_yml_file(file_path: str) -> Dict[str,List]:
    """
    Reads a yml from a given path in file_path argument
    """
    with open(file_path, "r", encoding="utf8") as stream:
        try:
            zfile = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            sys.exit()
    if "zranges" not in zfile:
        error_text = "The yaml zone file must be in the format:\nzranges:\
        \n    - Zone1: [1, 5]\n    - Zone2: [6, 10]\n    - Zone3: [11, 14])"
        raise Exception(error_text)
    return zfile

def main(arguments=None):
    """
    Takes input arguments and calculates co2 mass as a property and aggregates it to a 2D map
    at each time step, divided into different phases and locations.
    """
    if arguments is None:
        arguments = sys.argv[1:]
    config_ = _parser.process_arguments(arguments)

    if config_.input.properties:
        raise ValueError("CO2 mass computation does not take a property as input")
    if config_.co2_mass_settings is None:
        raise ValueError("CO2 mass computation needs co2_mass_settings as input")

    generate_co2_mass_maps(config_)


if __name__ == "__main__":
    main()
