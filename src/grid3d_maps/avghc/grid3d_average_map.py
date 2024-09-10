"""Script to make average maps directly from 3D grids.

A typical scenario is to create average maps directly from Eclipse
simulation files (or eventually other similators), but ROFF files
are equally supported.
"""

import logging
import sys

from . import (
    _compute_avg,
    _configparser,
    _get_grid_props,
    _get_zonation_filters,
    _mapsettings,
)

try:
    from grid3d_maps.version import __version__
except ImportError:
    __version__ = "0.0.0"

APPNAME = "grid3d_average_map"

# Module variables for ERT hook implementation:
DESCRIPTION = (
    "Make average property maps directly from 3D grids. Docs:\n"
    + "https://fmu-docs.equinor.com/docs/grid3d-maps/"
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def do_parse_args(args):
    """Parse command line arguments that will override config."""
    return _configparser.parse_args(args, APPNAME, DESCRIPTION)


def yamlconfig(inputfile, args):
    """Read from YAML file and modify/override"""

    config = _configparser.yconfig(inputfile)
    config = _configparser.prepare_metadata(config)
    config = _configparser.propformatting(config)

    # override with command line args
    config = _configparser.yconfig_override(config, args, APPNAME)

    config = _configparser.yconfig_set_defaults(config, APPNAME)

    # in case of YAML input (e.g. zonation from file)
    config = _configparser.yconfig_addons(config, APPNAME)

    if args.dumpfile:
        _configparser.yconfigdump(config, args.dumpfile)

    return config


def get_grid_props_data(config):
    """Collect the relevant Grid and props data (but not do the import)."""

    gfile, initlist, restartlist, dates = _get_grid_props.files_to_import(
        config, APPNAME
    )

    logger.info("Grid file is {}".format(gfile))

    logger.info("Getting INIT file data")
    for initpar, initfile in initlist.items():
        logger.info("%s file is %s", initpar, initfile)

    logger.info("Getting RESTART file data")
    for restpar, restfile in restartlist.items():
        logger.info("%s file is %s", restpar, restfile)

    logger.info("Getting dates")
    for date in dates:
        logger.info("Date is %s", date)

    return gfile, initlist, restartlist, dates


def import_pdata(config, gfile, initlist, restartlist, dates):
    """Import the data, and represent datas as numpies"""

    grd, initobjects, restobjects, dates = _get_grid_props.import_data(
        APPNAME, gfile, initlist, restartlist, dates
    )
    specd, averaged = _get_grid_props.get_numpies_avgprops(
        config, grd, initobjects, restobjects
    )

    # returns also dates since dates list may be updated after import
    return grd, specd, averaged, dates


def import_filters(config, grd):
    """Import the filter data properties, process and return a filter mask"""

    return _get_grid_props.import_filters(config, APPNAME, grd)


def get_zranges(config, grd):
    """Get the zonation names and ranges based on the config file.

    The zonation input has several variants; this is processed
    here. The config['zonation']['zranges'] is a list like

        - Tarbert: [1, 10]
        - Ness: [11,13]

    Args:
        config: The configuration dictionary
        grd (Grid): The XTGeo grid object

    Returns:
        A numpy zonation 3D array (zonation) + a zone dict)
    """
    zonation, zoned = _get_zonation_filters.zonation(config, grd)

    return zonation, zoned


def compute_avg_and_plot(
    config, grd, specd, propd, dates, zonation, zoned, filterarray
):
    """A dict of avg (numpy) maps, with zone name as keys."""

    if config["mapsettings"] is None:
        config = _mapsettings.estimate_mapsettings(config, grd)
    else:
        logger.info("Check map settings vs grid...")
        status = _mapsettings.check_mapsettings(config, grd)
        if status >= 10:
            logger.critical("STOP! Mapsettings defined is outside the 3D grid!")

    # This is done a bit different here than in the HC thickness. Here the
    # mapping and plotting is done within _compute_avg.py

    avgd = _compute_avg.get_avg(
        config, specd, propd, dates, zonation, zoned, filterarray
    )

    if config["output"]["plotfolder"] is not None:
        _compute_avg.do_avg_plotting(config, avgd)


def main(args=None):
    """Main routine."""
    logger.info(f"Starting {APPNAME} (version {__version__})")
    logger.info("Parse command line")
    args = do_parse_args(args)

    config = None
    if not args.config:
        logger.error("Config file is missing")
        sys.exit(1)

    logger.debug("--config option is applied, reading YAML ...")

    # get the configurations
    logger.info("Parse YAML file")
    config = yamlconfig(args.config, args)

    # get the files
    logger.info("Collect files...")
    gfile, initlist, restartlist, dates = get_grid_props_data(config)

    # import data from files and return relevant numpies
    logger.info("Import files...")

    grd, specd, propd, dates = import_pdata(config, gfile, initlist, restartlist, dates)

    # get the filter array
    filterarray = import_filters(config, grd)
    logger.info("Filter mean value: %s", filterarray.mean())
    if filterarray.mean() < 1.0:
        logger.info("Property filters are active")

    for prop, val in propd.items():
        logger.info("Key is %s, avg value is %s", prop, val.mean())

    # Get the zonations
    logger.info("Get zonation info")
    zonation, zoned = get_zranges(config, grd)

    logger.info("Compute average properties")
    compute_avg_and_plot(config, grd, specd, propd, dates, zonation, zoned, filterarray)


if __name__ == "__main__":
    main()
