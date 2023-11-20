import glob
import os
import sys
import tempfile
from typing import List, Optional

import xtgeo

from grid3d_maps.aggregate import (
    _config,
    _migration_time,
    _parser,
    grid3d_aggregate_map,
)

# Module variables for ERT hook implementation:
DESCRIPTION = (
    "Generate migration time property maps. Docs:\n"
    + "https://fmu-docs.equinor.com/docs/grid3d-maps/"
)
CATEGORY = "modelling.reservoir"
EXAMPLES = """
.. code-block:: console

  FORWARD_MODEL GRID3D_MIGRATION_TIME(<CONFIG_MIGTIME>=conf.yml, <ECLROOT>=<ECLBASE>)
"""


def calculate_migration_time_property(
    properties_files: str,
    property_name: Optional[str],
    lower_threshold: float,
    grid_file: Optional[str],
    dates: List[str],
):
    """
    Calculates a 3D migration time property from the provided grid and grid property
    files
    """
    prop_spec = [
        _config.Property(source=f, name=property_name)
        for f in glob.glob(properties_files, recursive=True)
    ]
    grid = None if grid_file is None else xtgeo.grid_from_file(grid_file)
    properties = _parser.extract_properties(prop_spec, grid, dates)
    t_prop = _migration_time.generate_migration_time_property(
        properties, lower_threshold
    )
    return t_prop


def migration_time_property_to_map(
    config_: _config.RootConfig,
    t_prop: xtgeo.GridProperty,
):
    """
    Aggregates and writes a migration time property to file using `grid3d_aggragte_map`.
    The migration time property is written to a temporary file while performing the
    aggregation.
    """
    config_.computesettings.aggregation = _config.AggregationMethod.MIN
    config_.output.aggregation_tag = False
    temp_file, temp_path = tempfile.mkstemp()
    os.close(temp_file)
    config_.input.properties.append(_config.Property(temp_path, None, None))
    t_prop.to_file(temp_path)
    grid3d_aggregate_map.generate_from_config(config_)
    os.unlink(temp_path)


def main(arguments=None):
    """
    Calculates a migration time property and aggregates it to a 2D map
    """
    if arguments is None:
        arguments = sys.argv[1:]
    config_ = _parser.process_arguments(arguments)
    if len(config_.input.properties) > 1:
        raise ValueError(
            "Migration time computation is only supported for a single property"
        )
    p_spec = config_.input.properties.pop()
    t_prop = calculate_migration_time_property(
        p_spec.source,
        p_spec.name,
        p_spec.lower_threshold,
        config_.input.grid,
        config_.input.dates,
    )
    migration_time_property_to_map(config_, t_prop)


if __name__ == "__main__":
    main()
