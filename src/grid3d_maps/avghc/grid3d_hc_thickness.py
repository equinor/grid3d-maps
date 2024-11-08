"""Script to make HC thickness maps directly from 3D grids.

A typical scenario is to create HC thickness maps directly from Eclipse
simulation files (or eventually other similators).

"""

import logging
import sys

from . import (
    _compute_hcpfz,
    _configparser,
    _get_grid_props,
    _get_zonation_filters,
    _hc_plotmap,
    _mapsettings,
)

try:
    from grid3d_maps.version import __version__
except ImportError:
    __version__ = "0.0.0"

APPNAME = "grid3d_hc_thickness"

# Module variables for ERT hook implementation:
DESCRIPTION = (
    "Make HC thickness maps directly from 3D grids. Docs:\n"
    + "https://fmu-docs.equinor.com/docs/grid3d-maps/"
)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def do_parse_args(args):
    return _configparser.parse_args(args, APPNAME, DESCRIPTION)


def yamlconfig(inputfile, args):
    """Read from YAML file and modify/override"""
    config = _configparser.yconfig(inputfile)
    config = _configparser.dateformatting(config)
    config = _configparser.prepare_metadata(config)

    # override with command line args
    config = _configparser.yconfig_override(config, args, APPNAME)

    config = _configparser.yconfig_set_defaults(config, APPNAME)

    # in case of YAML input (e.g. zonation from file)
    config = _configparser.yconfig_addons(config, APPNAME)
    config = _configparser.yconfig_metadata_hc(config)

    if args.dumpfile:
        _configparser.yconfigdump(config, args.dumpfile)

    return config


def get_grid_props_data(config):
    """Collect the relevant Grid and props data (but not do the import)."""

    gfile, initlist, restartlist, dates = _get_grid_props.files_to_import(
        config, APPNAME
    )

    logger.info("Grid file is {}".format(gfile))

    if initlist:
        logger.info("Getting INITIAL file data (as INIT or ROFF)")

        for initpar, initfile in initlist.items():
            logger.info("%s file is %s", initpar, initfile)

    if restartlist:
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

    # get the numpies
    initd, restartd = _get_grid_props.get_numpies_hc_thickness(
        config, grd, initobjects, restobjects, dates
    )

    # returns also dates since dates list may be updated after import

    return grd, initd, restartd, dates


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
        config (dict): The configuration dictionary
        grd (Grid): The XTGeo grid object

    Returns:
        A numpy zonation 3D array
    """
    zonation, zoned = _get_zonation_filters.zonation(config, grd)

    return zonation, zoned


def compute_hcpfz(config, initd, restartd, dates, hcmode, filterarray):
    return _compute_hcpfz.get_hcpfz(config, initd, restartd, dates, hcmode, filterarray)


def plotmap(config, grd, initd, hcpfzd, zonation, zoned, hcmode, filtermean=None):
    """Do checks, mapping and plotting"""

    # check if values looks OK. Status flag:
    # 0: Seems

    if config["mapsettings"] is None:
        config = _mapsettings.estimate_mapsettings(config, grd)
    else:
        logger.info("Check map settings vs grid...")
        status = _mapsettings.check_mapsettings(config, grd)
        if status >= 10:
            logger.critical("STOP! Mapsettings defined is outside the 3D grid!")

    mapzd = _hc_plotmap.do_hc_mapping(config, initd, hcpfzd, zonation, zoned, hcmode)

    if config["output"]["plotfolder"] is not None:
        _hc_plotmap.do_hc_plotting(config, mapzd, hcmode, filtermean=filtermean)


def main(args=None):
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
    grd, initd, restartd, dates = import_pdata(
        config, gfile, initlist, restartlist, dates
    )

    # get the filter array
    filterarray = import_filters(config, grd)
    logger.info("Filter mean value: %s", filterarray.mean())
    if filterarray.mean() < 1.0:
        logger.info("Property filters are active")

    # Get the zonations
    logger.info("Get zonation info")

    zonation, zoned = get_zranges(config, grd)

    if config["computesettings"]["mode"] == "both":
        hcmodelist = ["oil", "gas"]
    else:
        hcmodelist = [config["computesettings"]["mode"]]

    for hcmode in hcmodelist:
        logger.info("Compute HCPFZ property for {}".format(hcmode))
        hcpfzd = compute_hcpfz(config, initd, restartd, dates, hcmode, filterarray)

        logger.info("Do mapping...")
        plotmap(
            config,
            grd,
            initd,
            hcpfzd,
            zonation,
            zoned,
            hcmode,
            filtermean=filterarray.mean(),
        )


if __name__ == "__main__":
    main()
