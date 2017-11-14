# -*- coding: utf-8 -*-

"""Script to make average maps directly from 3D grids.

A typical scenario is to create average maps directly from Eclipse
simulation files (or eventually other similators), but ROFF files
are equally supported.

"""

from __future__ import division, print_function, absolute_import

import sys

from xtgeo.common import XTGeoDialog

from . import _configparser
from . import _get_grid_props
from . import _get_zonation_filters
from . import _compute_avg
from . import _mapsettings

from . import _version

appname = 'grid3d_average_map'

appdescr = 'Make average property maps directly from 3D grids'

__version__ = _version.get_versions()['version']

xtg = XTGeoDialog()

XTGeoDialog.print_xtgeo_header(appname, __version__)

logger = xtg.basiclogger(__name__)


def do_parse_args(args):

    args = _configparser.parse_args(args, appname, appdescr)

    return args


def yamlconfig(inputfile, args):
    """Read from YAML file and modify/override"""
    config = _configparser.yconfig(inputfile)

    # override with command line args
    config = _configparser.yconfig_override(config, args, appname)

    config = _configparser.yconfig_set_defaults(config, appname)

    # in case of YAML input (e.g. zonation from file)
    config = _configparser.yconfig_addons(config, appname)

    logger.info('Updated config:'.format(config))
    for name, val in config.items():
        logger.info('{}'.format(name))
        logger.info('{}'.format(val))

    return config


def get_grid_props_data(config, appname):
    """Collect the relevant Grid and props data (but not do the import)."""

    gfile, initlist, restartlist, dates = (
        _get_grid_props.files_to_import(config, appname))

    xtg.say('Grid file is {}'.format(gfile))

    xtg.say('Getting INIT file data')
    for initpar, initfile in initlist.items():
        logger.info('{} file is {}'.format(initpar, initfile))

    xtg.say('Getting RESTART file data')
    for restpar, restfile in restartlist.items():
        logger.info('{} file is {}'.format(restpar, restfile))

    xtg.say('Getting dates')
    for date in dates:
        logger.info('Date is {}'.format(date))

    return gfile, initlist, restartlist, dates


def import_pdata(config, appname, gfile, initlist, restartlist, dates):
    """Import the data, and represent datas as numpies"""

    grd, initobjects, restobjects, dates = (
        _get_grid_props.import_data(config, appname, gfile, initlist,
                                    restartlist, dates))
    specd, averaged = (
        _get_grid_props.get_numpies_avgprops(config, grd, initobjects,
                                             restobjects, dates))

    # returns also dates since dates list may be updated after import
    return grd, specd, averaged, dates


def get_zranges(config, dz):
    """Get the zonation names and ranges based on the config file.

    The zonation input has several variants; this is processed
    here. The config['zonation']['zranges'] is a list like

        - Tarbert: [1, 10]
        - Ness: [11,13]

    Args:
        config: The configuration dictionary
        dz: A numpy.ma for dz

    Returns:
        A numpy zonation 3D array (zonation) + a zone dict)
    """
    zonation, zoned = _get_zonation_filters.zonation(config, dz)

    logger.debug('Zonation avg is {}'.format(zonation.mean()))
    logger.debug('Zoned is {}'.format(zoned))

    return zonation, zoned


def compute_avg_and_plot(config, grd, specd, propd, dates, zonation, zoned):
    """A dict of avg (numpy) maps, with zone name as keys."""

    if config['mapsettings'] is None:
        config = _mapsettings.estimate_mapsettings(config, grd)
    else:
        xtg.say('Check map settings vs grid...')
        status = _mapsettings.check_mapsettings(config, grd)
        if status >= 10:
            xtg.critical('STOP! Mapsettings defined is outside the 3D grid!')

    # This is done a bit different here than in the HC thickness. Here the
    # mapping and plotting is done within _compute_avg.py

    avgd = _compute_avg.get_avg(config, specd, propd, dates, zonation, zoned)

    if config['output']['plotfolder'] is not None:
        _compute_avg.do_avg_plotting(config, avgd)


def main(args=None):

    xtg.say('Parse command line')
    args = do_parse_args(args)

    config = None
    if not args.config:
        xtg.error('Config file is missing')
        sys.exit(1)

    logger.debug('--config option is applied, reading YAML ...')

    # get the configurations
    xtg.say('Parse YAML file')
    config = yamlconfig(args.config, args)

    # get the files
    xtg.say('Collect files...')
    gfile, initlist, restartlist, dates = (
        get_grid_props_data(config, appname))

    # import data from files and return relevant numpies
    xtg.say('Import files...')

    grd, specd, propd, dates = import_pdata(config, appname, gfile, initlist,
                                            restartlist, dates)

    for prop, val in propd.items():
        logger.info('Key is {}, avg value is {}'.format(prop, val.mean()))

    # Get the zonations
    xtg.say('Get zonation info')
    dzp = specd['idz']
    zonation, zoned = get_zranges(config, dzp)

    xtg.say('Compute average properties')
    compute_avg_and_plot(config, grd, specd, propd, dates, zonation, zoned)


if __name__ == '__main__':
    main()
