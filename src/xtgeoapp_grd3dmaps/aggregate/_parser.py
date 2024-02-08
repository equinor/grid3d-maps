import argparse
import datetime
import pathlib
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import xtgeo
import yaml

from xtgeoapp_grd3dmaps.aggregate import _config
from xtgeoapp_grd3dmaps.aggregate._config import (
    CO2MassSettings,
    ComputeSettings,
    Input,
    MapSettings,
    Output,
    Property,
    RootConfig,
    Zonation,
    ZProperty,
)


def parse_arguments(arguments):
    """
    Uses argparse to parse arguments as expected from command line invocation
    """
    parser = argparse.ArgumentParser(__file__)
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=True,
        help="Config file on YAML format (required)",
    )
    parser.add_argument(
        "--mapfolder",
        help="Path to output map folder (overrides yaml file)",
        default=None,
    )
    parser.add_argument(
        "--plotfolder",
        help="Path to output plot folder (overrides yaml file)",
        default=None,
    )
    parser.add_argument(
        "--eclroot", help="Eclipse root name (includes case name)", default=None
    )
    parser.add_argument(
        "--folderroot",
        help="Folder root name ($-alias available in config file)",
        default=None,
    )
    return parser.parse_args(arguments)


def process_arguments(arguments) -> RootConfig:
    """
    Interprets and parses the provided arguments to an internal representation of input
    in the `RootConfig` class
    """
    parsed_args = parse_arguments(arguments)
    replacements = {}
    if parsed_args.eclroot is not None:
        replacements["eclroot"] = parsed_args.eclroot
    if parsed_args.folderroot is not None:
        replacements["folderroot"] = parsed_args.folderroot
    config = parse_yaml(
        parsed_args.config,
        parsed_args.mapfolder,
        parsed_args.plotfolder,
        replacements,
    )
    return config


def parse_yaml(
    yaml_file: Union[str],
    map_folder: Optional[str],
    plot_folder: Optional[str],
    replacements: Dict[str, str],
) -> RootConfig:
    """
    Parses a yaml file to a corresponding `RootConfig` object. See `load_yaml` for
    details.
    """
    config = load_yaml(yaml_file, map_folder, plot_folder, replacements)
    co2_mass_settings = (
        None
        if "co2_mass_settings" not in config
        else CO2MassSettings(**config.get("co2_mass_settings", {}))
    )
    return RootConfig(
        input=Input(**config["input"]),
        output=Output(**config["output"]),
        zonation=Zonation(**config.get("zonation", {})),
        computesettings=ComputeSettings(**config.get("computesettings", {})),
        mapsettings=MapSettings(**config.get("mapsettings", {})),
        co2_mass_settings=co2_mass_settings,
    )


def load_yaml(
    yaml_file: str,
    map_folder: Optional[str],
    plot_folder: Optional[str],
    replacements: Dict[str, str],
) -> Dict[str, Any]:
    """
    Loads a yaml config file. `replacements` is used to overwrite specific keywords in
    the file before parsing. `map_folder` and `plot_folder` can be used to override the
    corresponding keywords in the file.
    """
    with open(yaml_file, encoding="utf-8") as yml:
        content = yml.read()
    config = yaml.safe_load(content)
    for kw in ("eclroot", "folderroot"):
        if kw in config["input"] and kw not in replacements:
            replacements[kw] = config["input"][kw]
    for key, rep in replacements.items():
        content = content.replace(f"${key}", rep)
    if len(replacements) > 0:
        # Re-parse file content after replacements and remove keywords from "input" to
        # avoid unintended usages beyond this point
        config = yaml.safe_load(content)
        for key in replacements.keys():
            config["input"].pop(key, None)
    if map_folder is not None:
        config["output"]["mapfolder"] = map_folder
    if plot_folder is not None:
        config["output"]["plotfolder"] = plot_folder
    # Handle things that is implemented in avghc, but not in this module
    redundant_keywords = set(config["input"].keys()).difference(
        {"properties", "grid", "dates"}
    )
    if redundant_keywords:
        raise ValueError(
            "The 'input' section only allows keywords 'properties' and 'grid'."
            " Keywords 'dates' and 'diffdates' are not implemented for this action."
            " Keywords representing properties must be defined under 'properties' for"
            f" this action. Redundant keywords: {', '.join(redundant_keywords)}"
        )
    if "filters" in config:
        raise NotImplementedError("Keyword 'filters' is not supported by this action")
    if "superranges" in config.get("zonation", {}):
        raise NotImplementedError(
            "Keyword 'superranges' is not supported by this action"
        )
    return config


def extract_properties(
    property_spec: Optional[List[Property]],
    grid: Optional[xtgeo.Grid],
    dates: List[str],
) -> List[xtgeo.GridProperty]:
    """
    Extract 3D grid properties based on the provided property specification
    """
    properties: List[Property] = []
    if property_spec is None:
        return properties
    for spec in property_spec:
        try:
            names = "all" if spec.name is None else [spec.name]
            props = xtgeo.gridproperties_from_file(
                spec.source,
                names=names,
                grid=grid,
                dates=dates or "all",
            ).props
        except (RuntimeError, ValueError):
            props = [xtgeo.gridproperty_from_file(spec.source, name=spec.name)]
        if spec.lower_threshold is not None:
            for prop in props:
                prop.values.mask[prop.values < spec.lower_threshold] = True
        # Check if any of the properties missing a date had date as part of the file
        # stem, separated by a "--"
        for prop in props:
            if prop.date is None and "--" in spec.source:
                date = pathlib.Path(spec.source.split("--")[-1]).stem
                try:
                    # Make sure time stamp is on a valid format
                    datetime.datetime.strptime(date, "%Y%m%d")
                except ValueError:
                    continue
                prop.date = date
                prop.name += f"--{date}"
        if len(dates) > 0:
            props = [p for p in props if p.date in dates]
        properties += props
    return properties


def extract_zonations(
    zonation: Zonation, grid: xtgeo.Grid
) -> List[Tuple[str, np.ndarray]]:
    """
    Extract boolean zonation arrays and corresponding names based on `zonation`
    """
    if zonation.zproperty is None:
        return _zonation_from_zranges(grid, zonation.zranges)
    return _zonation_from_zproperty(grid, zonation.zproperty)


def _zonation_from_zranges(grid: xtgeo.Grid, z_ranges) -> List[Tuple[str, np.ndarray]]:
    actnum = grid.actnum_indices
    zones = []
    k = grid.get_ijk()[2].values1d[actnum]
    for z_def in z_ranges:
        for z_name, zr in z_def.items():
            zones.append((z_name, (zr[0] <= k) & (k <= zr[1])))
    return zones


def _zonation_from_zproperty(
    grid: xtgeo.Grid, zproperty: ZProperty
) -> List[Tuple[str, np.ndarray]]:
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
        zranges = zfile["zranges"]
        return _zonation_from_zranges(grid, zranges)
    actnum = grid.actnum_indices
    prop = xtgeo.gridproperty_from_file(
        zproperty.source, grid=grid, name=zproperty.name
    )
    assert prop.isdiscrete
    if len(zproperty.zones) == 0:
        # Return definition for all zones extracted from the property file
        return [
            (f_name, prop.values1d[actnum] == f_code)
            for f_code, f_name in prop.codes.items()
            if f_name != ""
        ]
    return [
        (z_name, np.isin(prop.values1d[actnum], z_codes))
        for zone_def in zproperty.zones
        for z_name, z_codes in zone_def.items()
    ]


def create_map_template(
    map_settings: _config.MapSettings,
) -> Union[xtgeo.RegularSurface, float]:
    """
    Creates the map template to use based on the provided settings. May instead return a
    float value that is intended as a pixel-to-cell-size ratio to be used later for
    automatically calculating a map template based on the grid extents.
    """
    if map_settings.templatefile is not None:
        surf = xtgeo.surface_from_file(map_settings.templatefile)
        if surf.rotation != 0.0:
            raise NotImplementedError("Rotated surfaces are not handled correctly yet")
        return surf
    if map_settings.xori is not None:
        surf_kwargs = dict(
            ncol=map_settings.ncol,
            nrow=map_settings.nrow,
            xinc=map_settings.xinc,
            yinc=map_settings.yinc,
            xori=map_settings.xori,
            yori=map_settings.yori,
        )
        if not all((s is not None for s in surf_kwargs.values())):
            missing = [k for k, v in surf_kwargs.items() if v is None]
            raise ValueError(
                f"Failed to create map template due to partial map specification. "
                f"Missing: {', '.join(missing)}"
            )
        return xtgeo.RegularSurface(**surf_kwargs)
    return map_settings.pixel_to_cell_ratio
