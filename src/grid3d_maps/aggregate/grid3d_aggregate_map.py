import pathlib
import sys
from typing import List

import numpy as np
import xtgeo
from xtgeo.common import XTGeoDialog

from grid3d_maps.aggregate._config import (
    AggregationMethod,
    ComputeSettings,
    Input,
    MapSettings,
    Output,
    Zonation,
)
from grid3d_maps.aggregate._parser import (
    create_map_template,
    extract_properties,
    extract_zonations,
    process_arguments,
)

from . import _config, _grid_aggregation

_XTG = XTGeoDialog()


# Module variables for ERT hook implementation:
DESCRIPTION = (
    "Aggregate property maps from 3D grids. Docs:\n"
    + "https://fmu-docs.equinor.com/docs/grid3d-maps/"
)
CATEGORY = "modelling.reservoir"
EXAMPLES = """
.. code-block:: console

  FORWARD_MODEL GRID3D_AGGREGATE_MAP(<CONFIG_AGGREGATE>=conf.yml, <ECLROOT>=<ECLBASE>)
"""


def write_map(x_nodes, y_nodes, map_, filename):
    """
    Writes a 2D map to file as an xtgeo.RegularSurface. Returns the xtgeo.RegularSurface
    instance.
    """
    dx = x_nodes[1] - x_nodes[0]
    dy = y_nodes[1] - y_nodes[0]
    masked_map = np.ma.array(map_)
    masked_map.mask = np.isnan(map_)
    surface = xtgeo.RegularSurface(
        ncol=x_nodes.size,
        nrow=y_nodes.size,
        xinc=dx,
        yinc=dy,
        xori=x_nodes[0],
        yori=y_nodes[0],
        values=masked_map,
    )
    surface.to_file(filename)
    return surface


def write_plot_using_plotly(surf: xtgeo.RegularSurface, filename):
    """
    Writes a 2D map to an html using the plotly library
    """
    # pylint: disable=import-outside-toplevel
    import plotly.express as px

    x_nodes = surf.xori + np.arange(0, surf.ncol) * surf.xinc
    y_nodes = surf.yori + np.arange(0, surf.nrow) * surf.yinc
    px.imshow(
        surf.values.filled(np.nan).T, x=x_nodes, y=y_nodes, origin="lower"
    ).write_html(filename.with_suffix(".html"), include_plotlyjs="cdn")


def write_plot_using_quickplot(surface, filename):
    """
    Writes a 2D map using quickplot from xtgeoviz
    """
    # pylint: disable=import-outside-toplevel
    from xtgeoviz import quickplot

    quickplot(surface, filename=filename.with_suffix(".png"))


def generate_maps(
    input_: Input,
    zonation: Zonation,
    computesettings: ComputeSettings,
    map_settings: MapSettings,
    output: Output,
):
    """
    Calculate and write aggregated property maps to file
    """
    _XTG.say("Reading grid, properties and zone(s)")
    grid = xtgeo.grid_from_file(input_.grid)
    properties = extract_properties(input_.properties, grid, input_.dates)
    _filters = []
    if computesettings.all:
        _filters.append(("all", None))
    if computesettings.zone:
        _filters += extract_zonations(zonation, grid)
    _XTG.say("Generating Property Maps")
    xn, yn, p_maps = _grid_aggregation.aggregate_maps(
        create_map_template(map_settings),
        grid,
        properties,
        [f[1] for f in _filters],
        computesettings.aggregation,
        computesettings.weight_by_dz,
    )
    prop_tags = [
        _property_tag(p.name, computesettings.aggregation, output.aggregation_tag)
        for p in properties
    ]
    surfs = _ndarray_to_regsurfs(
        [f[0] for f in _filters],
        prop_tags,
        xn,
        yn,
        p_maps,
        output.lowercase,
    )
    _write_surfaces(surfs, output.mapfolder, output.plotfolder, output.use_plotly)


def _property_tag(prop: str, agg_method: AggregationMethod, agg_tag: bool):
    agg = f"{agg_method.value}_" if agg_tag else ""
    return f"{agg}{prop.replace('_', '--')}"


def _ndarray_to_regsurfs(
    filter_names: List[str],
    prop_names: List[str],
    x_nodes: np.ndarray,
    y_nodes: np.ndarray,
    maps: List[List[np.ndarray]],
    lowercase: bool,
) -> List[xtgeo.RegularSurface]:
    return [
        xtgeo.RegularSurface(
            ncol=x_nodes.size,
            nrow=y_nodes.size,
            xinc=x_nodes[1] - x_nodes[0],
            yinc=y_nodes[1] - y_nodes[0],
            xori=x_nodes[0],
            yori=y_nodes[0],
            values=np.ma.array(map_, mask=np.isnan(map_)),
            name=_deduce_surface_name(fn, prop, lowercase),
        )
        for fn, inner in zip(filter_names, maps)
        for prop, map_ in zip(prop_names, inner)
    ]


def _deduce_surface_name(filter_name, property_name, lowercase):
    name = f"{filter_name}--{property_name}"
    if lowercase:
        name = name.lower()
    return name


def _write_surfaces(
    surfaces: List[xtgeo.RegularSurface],
    map_folder: str,
    plot_folder: str,
    use_plotly: bool,
):
    for surface in surfaces:
        surface.to_file((pathlib.Path(map_folder) / surface.name).with_suffix(".gri"))
        if plot_folder:
            pn = pathlib.Path(plot_folder) / surface.name
            if use_plotly:
                write_plot_using_plotly(surface, pn)
            else:
                write_plot_using_quickplot(surface, pn)


def generate_from_config(config: _config.RootConfig):
    """
    Wrapper around `generate_maps` based on a configuration object (RootConfig)
    """
    generate_maps(
        config.input,
        config.zonation,
        config.computesettings,
        config.mapsettings,
        config.output,
    )


def main(arguments=None):
    """
    Main function that wraps `generate_from_config` with argument parsing
    """
    if arguments is None:
        arguments = sys.argv[1:]
    generate_from_config(process_arguments(arguments))


if __name__ == "__main__":
    main()
