import pathlib
import sys
from typing import List

import xtgeo
import numpy as np
from xtgeo.common import XTGeoDialog

from xtgeoviz import quickplot

from xtgeoapp_grd3dmaps.aggregate._config import (
    Property,
    MapSettings,
    Zonation,
    ComputeSettings,
)
from xtgeoapp_grd3dmaps.aggregate._parser import (
    extract_properties,
    process_arguments,
    create_map_template, extract_zonations,
)
from . import _grid_aggregation, _config

_XTG = XTGeoDialog()


# Module variables for ERT hook implementation:
DESCRIPTION = (
    "Aggregate property maps from 3D grids. Docs:\n"
    + "https://fmu-docs.equinor.com/docs/xtgeoapp-grd3dmaps/"
)
CATEGORY = "modelling.reservoir"
EXAMPLES = """
.. code-block:: console

  FORWARD_MODEL GRID3D_AGGREGATE_MAP(<CONFIG_AGGMAP>=conf.yml, <ECLROOT>=<ECLBASE>)
"""


def write_map(xn, yn, map_, filename):
    dx = xn[1] - xn[0]
    dy = yn[1] - yn[0]
    masked_map = np.ma.array(map_)
    masked_map.mask = np.isnan(map_)
    surface = xtgeo.RegularSurface(
        ncol=xn.size,
        nrow=yn.size,
        xinc=dx,
        yinc=dy,
        xori=xn[0],
        yori=yn[0],
        values=masked_map,
    )
    surface.to_file(filename)
    return surface


def write_plot_using_plotly(xn, yn, map_, filename):
    import plotly.express as px
    px.imshow(
        map_.T, x=xn, y=yn, origin="lower"
    ).write_html(filename.with_suffix('.html'), include_plotlyjs="cdn")


def write_plot_using_quickplot(surface, filename):
    quickplot(surface, filename=filename.with_suffix('.png'))


def deduce_map_filename(filter_name, agg_method, property_name, aggregation_tag):
    agg = f"{agg_method.value}_" if aggregation_tag else ""
    fn = f"{filter_name}--{agg}{property_name.replace('_', '--')}.gri"
    return fn


def generate_maps(
    grid_name: str,
    property_spec: List[Property],
    zonation: Zonation,
    computesettings: ComputeSettings,
    output_directory: str,
    map_settings: MapSettings,
    plot_directory: str,
    use_plotly: bool,
    aggregation_tag: bool,
):
    _XTG.say("Reading Grid")
    grid = xtgeo.grid_from_file(grid_name)
    _XTG.say("Reading properties")
    properties = extract_properties(property_spec, grid)
    _XTG.say("Reading Zones")
    _filters = []
    if computesettings.all:
        _filters.append(("all", None))
    if computesettings.zone:
        _filters += extract_zonations(zonation, grid)
    _XTG.say("Setting up map template")
    map_template = create_map_template(map_settings)
    _XTG.say("Generating Property Maps")
    xn, yn, p_maps = _grid_aggregation.aggregate_maps(
        map_template,
        grid,
        properties,
        [f[1] for f in _filters],
        computesettings.aggregation,
        computesettings.weight_by_dz,
    )
    assert len(_filters) == len(p_maps)
    for filter_, f_maps in zip(_filters, p_maps):
        f_name = filter_[0]
        # Max saturation maps
        assert len(properties) == len(f_maps)
        for prop, map_ in zip(properties, f_maps):
            fn = deduce_map_filename(
                f_name, computesettings.aggregation, prop.name, aggregation_tag
            )
            surface = write_map(xn, yn, map_, pathlib.Path(output_directory) / fn)
            if plot_directory:
                pn = (pathlib.Path(plot_directory) / fn).with_suffix('')
                if use_plotly:
                    write_plot_using_plotly(xn, yn, map_, pn)
                else:
                    write_plot_using_quickplot(surface, pn)


def generate_from_config(config: _config.RootConfig):
    generate_maps(
        config.input.grid,
        config.input.properties,
        config.zonation,
        config.computesettings,
        config.output.mapfolder,
        config.mapsettings,
        config.output.plotfolder,
        config.output.use_plotly,
        config.output.aggregation_tag,
    )


def main(arguments=None):
    if arguments is None:
        arguments = sys.argv[1:]
    generate_from_config(process_arguments(arguments))


if __name__ == '__main__':
    main()
