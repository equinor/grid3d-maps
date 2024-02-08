#!/usr/bin/env python

import time

import os
import sys
import tempfile
import xtgeo
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

    _input = config_.input
    co2_mass_settings = config_.co2_mass_settings
    _output = config_.output
    zonation = config_.zonation


    print(zonation)

    zones = co2_mass_settings.zones
    if zones is not None and isinstance(zones, str):
        co2_mass_settings.zones = [zones]

    print(co2_mass_settings)

    grid_file = _input.grid

    dates = _input.dates

    co2_data = calculate_co2(grid_file,co2_mass_settings.unrst_source,"mass",co2_mass_settings.init_source,None)    

    if len(dates)>0:
        co2_data.data_list = [x for x in co2_data.data_list if x.date in dates]

    print("Done calculating co2_data")

    out_property_list = _co2_mass.translate_co2data_to_property(
        co2_data,
        grid_file,
        co2_mass_settings,
        PROPERTIES_TO_EXTRACT,
        _output.mapfolder + "/grid",
    )


    print(zonation.zranges)
    print(co2_mass_settings)

    ## If all=Yes, get all the ranges from the zonation, good when zranges, missing the other part
    if config_.computesettings.all:
        if zonation.zranges is not None:
            zranges_limits = [list(d.values())[0] for d in zonation.zranges]
        elif zonation.Property is not None:
            if zproperty.source.split(".")[-1] in ["yml", "yaml"]:
                with open(zproperty.source, "r", encoding="utf8") as stream:
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
        max_zvalue = max(sublist[-1] for sublist in zranges_limits)
        min_zvalue = min(sublist[0] for sublist in zranges_limits)
        all_zrange = [min_zvalue, max_zvalue]
               

    config_.zonation.zranges = define_zones_to_plot(zonation,co2_mass_settings)

    print(config_.zonation.zranges)#.append({'all',all_zrange})


    if config_.computesettings.all:
        tmp_zranges= config_.zonation.zranges
        tmp_zranges.append({'all':all_zrange})
        config_.zonation.zranges = tmp_zranges
        config_.computesettings.all = False
        if not config_.computesettings.zone:
            config_.computesettings.zone = True
            #Remove whatever is not 'all'
            config_.zonation.zranges = [zrange for zrange in config_.zonation.zranges if 'all' in zrange]
        


    print(config_.zonation.zranges)#.append({'all',all_zrange})


    print(config_)

    print("Getting into the last stage")
    co2_mass_property_to_map(config_,out_property_list)

  
    """
    config_.input.properties = []
    config_.computesettings.aggregation = _config.AggregationMethod.SUM
    config_.output.aggregation_tag = False
    _, temp_path = tempfile.mkstemp()
    config_.input.properties.append(_config.Property(temp_path, None, None))
    print("Done here?")
    return out_property_list
    """


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
                print(prop)
                print(prop.date)
                #co2_mass_property_to_map(config_, prop)                
                print("This is very relevant")
                config_.input.properties.append(_config.Property(config_.output.mapfolder+"/grid/"+prop.name+"--"+prop.date+".roff", None, None))
                #print(config_)
                
    print("**** VERY IMPORTANT: printing config_ ****")
    print(config_)
    print("Trying a hack without affecting the existing code in grid3d_aggregate_map")
    #config_.computesettings.all = False
    #config_.computesettings.zone = True
    print("This is how config_.zonation looks like")
    print(config_.zonation)
    #config_.zonation = ##Add all to the zonation with all the range in the required format:), remove everything else

    grid3d_aggregate_map.generate_from_config(config_)


def define_zones_to_plot(
        zonation: _config.Zonation,
        co2_mass_settings: _config.CO2MassSettings,
):
    """
    Based on the zones defined in CO2MassSettings determine for which zones maps are produced
    """

    if zonation.zranges is not None :
        zone_names = [list(item.keys())[0] for item in zonation.zranges]    
    elif zonation.Property is not None :
        if zproperty.source.split(".")[-1] in ["yml", "yaml"]:
            with open(zproperty.source, "r", encoding="utf8") as stream:
                try:
                    zfile = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    print(exc)
                    sys.exit()
            if "zranges" not in zfile:
                error_text = "The yaml zone file must be in the format:\nzranges:\
                \n    - Zone1: [1, 5]\n    - Zone2: [6, 10]\n    - Zone3: [11, 14])"
                raise Exception(error_text)            
            zone_names = [list(item.keys())[0] for item in zfile.zranges]    
        

    if co2_mass_settings.zones is not None:
        zones_to_plot = [zone for zone in co2_mass_settings.zones if zone in zone_names]
        if len(zones_to_plot)==0:
            print("The zones specified in CO2 mass settings are not part of the zonation provided \n maps will be exported for all the existing zones")
        else:
            return( [item for item in zonation.zranges if list(item.keys())[0] in zones_to_plot])

    
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
    #out_property_list = calculate_mass_property(config_)

    start_time = time.time()
    generate_co2_mass_maps(config_)
    end_time = time.time()

    execution_time = end_time - start_time
    print("Execution time: ", execution_time, "seconds")

    """
        config_.input,
        config_.co2_mass_settings,
        config_.output
    )
    define_zones_to_plot(config_)
    print("Checking out some consistency here")
    print("len(out_property_list)="+str(len(out_property_list)))
    print("len(out_property_list[0])="+str(len(out_property_list[0])))
    print("len(out_property_list[1])="+str(len(out_property_list[1])))
    print("len(out_property_list[2])="+str(len(out_property_list[2])))
    print(out_property_list[1][0])
    print((out_property_list[1][0].date))

    ##Until here we seem to be safe. However, there seems to be a more serious issue as when we export the properti(es). The date is not read afterwards

    ##Idea: Improve the creation of the properties in calculate_mass_property and see if the feature "date" is recovered back when reading the property
     
    for props in out_property_list:
        if len(props)>0 :
            for prop in props:
                print(prop)
                print(prop.date)
                #co2_mass_property_to_map(config_, prop)
    """


if __name__ == "__main__":
    main()
