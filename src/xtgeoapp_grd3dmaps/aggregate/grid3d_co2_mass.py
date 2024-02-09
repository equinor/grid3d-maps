#!/usr/bin/env python
import os
import sys
import tempfile
import xtgeo
import yaml
from typing import List, Optional
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
    #-> List[List[xtgeo.GridProperty]]:

    Calculates and exports 3D CO2 mass properties from the provided grid and config files

    Args:
        grid_file (str): Path to EGRID-file
        co2_mass_settings (CO2MassSettings): Settings from config file for calculation
                                             of CO2 mass maps.
        out_folder (str): Path to store the produced 3D GridProperties.


    Returns:
        List[List[xtgeo.GridProperty].

    """

    co2_mass_settings = config_.co2_mass_settings
    zonation = config_.zonation
    zones = co2_mass_settings.zones
    if zones is not None and isinstance(zones, str):
        co2_mass_settings.zones = [zones]

    grid_file = config_.input.grid
    co2_data = calculate_co2(grid_file,co2_mass_settings.unrst_source,"mass",co2_mass_settings.init_source,None)    

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

    if config_.computesettings.all: 
        if len(zonation.zranges)>0:             
            all_zrange = find_all_zrange(zonation=zonation)
        else:
            all_zrange = find_all_zrange(grid_file=grid_file)

    if len(zonation.zranges)>0 or zonation.zproperty is not None:       
        config_.zonation.zranges = define_zones_to_plot(zonation,co2_mass_settings)
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
    Aggregates with SUM and writes a CO2 mass property to file using `grid3d_aggregate_map`.
    The property is written to a temporary file while performing the
    aggregation.

    Args:
        config_: Arguments in the config file
        t_prop: Grid property to be aggregated

    """
    config_.input.properties = []
    config_.computesettings.aggregation = _config.AggregationMethod.SUM
    config_.output.aggregation_tag = False

    for props in property_list:
        if len(props)>0 :
            for prop in props:
                config_.input.properties.append(_config.Property(config_.output.mapfolder+"/grid/"+prop.name+"--"+prop.date+".roff", None, None))
                
    grid3d_aggregate_map.generate_from_config(config_)


def define_zones_to_plot(
        zonation: _config.Zonation,
        co2_mass_settings: _config.CO2MassSettings,
):
    """
    Based on the zones defined in CO2MassSettings determine for which zones maps are produced
    """

    if len(zonation.zranges) > 0 :
        zone_names = [list(item.keys())[0] for item in zonation.zranges]    
    elif zonation.zproperty is not None :
        if zonation.zproperty.source.split(".")[-1] in ["yml", "yaml"]:
            with open(zonation.zproperty.source, "r", encoding="utf8") as stream:
                try:
                    zfile = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    print(exc)
                    sys.exit()
            if "zranges" not in zfile:
                error_text = "The yaml zone file must be in the format:\nzranges:\
                \n    - Zone1: [1, 5]\n    - Zone2: [6, 10]\n    - Zone3: [11, 14])"
                raise Exception(error_text) 
            zonation.zranges = zfile['ranges']
            zone_names = [list(item.keys())[0] for item in zonation.zranges]    
        

    if co2_mass_settings.zones is not None:
        zones_to_plot = [zone for zone in co2_mass_settings.zones if zone in zone_names]
        if len(zones_to_plot)==0:
            print("The zones specified in CO2 mass settings are not part of the zonation provided \n maps will be exported for all the existing zones")
        else:
            return([item for item in zonation.zranges if list(item.keys())[0] in zones_to_plot])
    else:
        return(zonation.zranges)

def find_all_zrange(
        zonation: Optional[_config.Zonation] = None,
        grid_file: Optional[str] = None,
):
    if zonation is not None:
        if len(zonation.zranges) > 0:
            zranges_limits = [list(d.values())[0] for d in zonation.zranges]
        elif zonation.zproperty is not None:
            if zonation.zproperty.source.split(".")[-1] in ["yml", "yaml"]:
                with open(zonation.zproperty.source, "r", encoding="utf8") as stream:
                    try:
                        zfile = yaml.safe_load(stream)
                    except yaml.YAMLError as exc:
                        print(exc)
                        sys.exit()
                if "zranges" not in zfile:
                    error_text = "The yaml zone file must be in the format:\nzranges:\
                    \n    - Zone1: [1, 5]\n    - Zone2: [6, 10]\n    - Zone3: [11, 14])"
                    raise Exception(error_text)            
            zranges_limits = [list(d.values())[0] for d in zfile.zranges]
    elif grid_file is not None:
        grid_pf = xtgeo.grid_from_file(grid_file)
        dimensions = (grid_pf.ncol, grid_pf.nrow, grid_pf.nlay)
        zranges_limits = [[1,grid_pf.nlay]]
    else:
        error_text = "Either zonation or grid_file need to be provided"
        raise Exception(error_text)            

    max_zvalue = max(sublist[-1] for sublist in zranges_limits)
    min_zvalue = min(sublist[0] for sublist in zranges_limits)
    all_zrange = [min_zvalue, max_zvalue]
    return(all_zrange)                      
    
def main(arguments=None):
    """
    Takes input arguments and calculates co2 mass as a property and aggregates it to a 2D map
    at each time step, divided into different phases and locations(TODO).
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
