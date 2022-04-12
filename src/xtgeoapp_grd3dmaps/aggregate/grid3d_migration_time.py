import os
import sys
import glob
import tempfile
from typing import Optional
import xtgeo

from xtgeoapp_grd3dmaps.aggregate import (
    grid3d_aggregate_map,
    _migration_time,
    _config,
    _parser,
)


def calculate_migration_time_property(
    properties_files: str,
    property_name: Optional[str],
    lower_threshold: float,
    grid_file: Optional[str],
):
    prop_spec = [
        _config.Property(source=f, name=property_name)
        for f in glob.glob(properties_files, recursive=True)
    ]
    grid = None if grid_file is None else xtgeo.grid_from_file(grid_file)
    properties = _parser.extract_properties(prop_spec, grid)
    t_prop = _migration_time.generate_migration_time_property(
        properties, lower_threshold
    )
    return t_prop


def main(arguments=None):
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
    )
    # Use temporary file for t_prop while executing aggregation
    config_.computesettings.aggregation = _config.AggregationMethod.MIN
    config_.output.aggregation_tag = False
    temp_file, temp_path = tempfile.mkstemp()
    os.close(temp_file)
    config_.input.properties.append(_config.Property(temp_path, None, None))
    t_prop.to_file(temp_path)
    grid3d_aggregate_map.generate_from_config(config_)
    os.unlink(temp_path)


if __name__ == '__main__':
    main()
