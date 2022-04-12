import argparse
import datetime
import pathlib
from typing import List, Optional, Tuple, Union, Dict, Any

import numpy as np
import xtgeo
import yaml

from xtgeoapp_grd3dmaps.aggregate import _config
from xtgeoapp_grd3dmaps.aggregate._config import (
    Property,
    RootConfig,
    Input,
    Output,
    ComputeSettings,
    MapSettings, Zonation
)


def parse_arguments(arguments):
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
        default=None
    )
    parser.add_argument(
        "--plotfolder",
        help="Path to output plot folder (overrides yaml file)",
        default=None
    )
    parser.add_argument(
        "--eclroot",
        help="Eclipse root name (includes case name)",
        default=None
    )
    parser.add_argument(
        "--folderroot",
        help="Folder root name ($-alias available in config file)",
        default=None
    )
    return parser.parse_args(arguments)


def process_arguments(arguments) -> RootConfig:
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
    config = load_yaml(yaml_file, map_folder, plot_folder, replacements)
    return RootConfig(
        input=Input(**config["input"]),
        output=Output(**config["output"]),
        zonation=Zonation(**config.get("zonation", {})),
        computesettings=ComputeSettings(**config.get("computesettings", {})),
        mapsettings=MapSettings(**config.get("mapsettings", {})),
    )


def load_yaml(
    yaml_file: str,
    map_folder: Optional[str],
    plot_folder: Optional[str],
    replacements: Dict[str, str],
) -> Dict[str, Any]:
    content = open(yaml_file).read()
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
    redundant_keywords = set(config["input"].keys()).difference({"properties", "grid"})
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
    property_spec: List[Property], grid: Optional[xtgeo.Grid]
) -> List[xtgeo.GridProperty]:
    properties = []
    for spec in property_spec:
        try:
            names = "all" if spec.name is None else [spec.name]
            props = xtgeo.gridproperties_from_file(
                spec.source, names=names, grid=grid, dates="all",
            ).props
        except (RuntimeError, ValueError):
            props = [xtgeo.gridproperty_from_file(spec.source, name=spec.name)]
        if spec.lower_threshold is not None:
            for p in props:
                p.values.mask[p.values < spec.lower_threshold] = True
        # Check if any of the properties missing a date had date as part of the file
        # stem, separated by a "--"
        for p in props:
            if p.date is None and "--" in spec.source:
                d = pathlib.Path(spec.source.split("--")[-1]).stem
                try:
                    # Make sure time stamp is on a valid format
                    datetime.datetime.strptime(d, "%Y%m%d")
                except ValueError:
                    continue
                p.date = d
                p.name += f"--{d}"
        properties += props
    return properties


def extract_zonations(
    zonation: Zonation,
    grid: xtgeo.Grid
) -> List[Tuple[str, np.ndarray]]:
    zones = []
    actnum = grid.actnum_indices
    if zonation.zproperty is not None:
        prop = xtgeo.gridproperty_from_file(
            zonation.zproperty.source, grid=grid, name=zonation.zproperty.name
        )
        assert prop.isdiscrete
        for f_code, f_name in prop.codes.items():
            if f_name == "":
                continue
            zones.append((f_name, prop.values1d[actnum] == f_code))
    else:
        k = grid.get_ijk()[2].values1d[actnum]
        for z_def in zonation.zranges:
            for z_name, zr in z_def.items():
                zones.append((z_name, (zr[0] <= k) & (k <= zr[1])))
    return zones


def create_map_template(
    map_settings: _config.MapSettings
) -> Union[xtgeo.RegularSurface, float]:
    if map_settings.templatefile is not None:
        surf = xtgeo.surface_from_file(map_settings.templatefile)
        if surf.rotation != 0.0:
            raise NotImplementedError("Rotated surfaces are not handled correctly yet")
        return surf
    elif map_settings.xori is not None:
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
    else:
        return map_settings.pixel_to_cell_ratio
