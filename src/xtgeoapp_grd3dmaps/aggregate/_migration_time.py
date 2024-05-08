import datetime
from typing import List, Union

import numpy as np
import xtgeo

MIGRATION_TIME_PNAME = "MigrationTime"


def generate_migration_time_property(
    co2_props: List[xtgeo.GridProperty],
    co2_threshold: Union[float,List],
):
    """
    Calculates a 3D grid property reflecting the migration time. Migration time is
    defined as the first time step at which the property value exceeds the provided
    `lower_threshold`.
    """
    # Calculate time since simulation start
    times = [datetime.datetime.strptime(_prop.date, "%Y%m%d") for _prop in co2_props]
    time_since_start = [(t - times[0]).days / 365 for t in times]
    # Duplicate first property to ensure equal actnum
    prop_names = [prop.name.split("--")[0] for prop in co2_props]
    unique_prop_names = list(set(prop_names))
    props_idx = {}
    first_prop_idx = {}
    if isinstance(co2_threshold,float):
        co2_threshold = [co2_threshold]
    if len(co2_threshold) != len(unique_prop_names):
        if len(co2_threshold) == 1:
            print("Only one value of co2_threshold for " + str(len(unique_prop_names)) + " properties. The same threshold will be assumed for all the properties")
            co2_threshold = [co2_threshold[0] for x in unique_prop_names]
        else:
            error_text = str(len(co2_threshold)) + " values of co2_threshold provided, but " + str(len(unique_prop_names)) + " properties in config file input\nfix the amount of values in co2_threshold or the amount of properties in config file"
            raise Exception(error_text)
    co2_thresholds = {}
    for index, value in enumerate(prop_names):
        if value not in props_idx:
            props_idx[value] = [index]
            co2_thresholds[value] = co2_threshold[len(co2_thresholds)]
            first_prop_idx[value] = index
        else:
            props_idx[value].append(index)
    t_props = {prop_name:co2_props[first_prop_idx[prop_name]].copy(newname=MIGRATION_TIME_PNAME + "_" + prop_name) for prop_name in unique_prop_names}
    for name in unique_prop_names:
        t_props[name].values[~t_props[name].values.mask] = np.inf
        for co2, dt in zip([co2_props[i] for i in props_idx[name]], [time_since_start[i] for i in props_idx[name]]):
            above_threshold = co2.values > float(co2_thresholds[name])
            t_props[name].values[above_threshold] = np.minimum(t_props[name].values[above_threshold], dt)
        # Mask inf values
        t_props[name].values.mask[np.isinf(t_props[name].values)] = 1
    return t_props
