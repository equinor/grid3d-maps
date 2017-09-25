# -*- coding: utf-8 -*-

"""Script to make HC thickness maps directly from 3D grids.

A typical scenario is to create HC thickness maps directly from Eclipse
simulation files (or eventually other similators).

"""

from __future__ import division, print_function, absolute_import

import sys
import logging

from xtgeo.common import XTGeoDialog

from . import _configparser
from . import _get_grid_props
from . import _get_zonation_filters
from . import _compute_hcpfz
from . import _plotmap

from . import _version

appname = 'grid3d_hc_thickness'

appdescr = 'Make HC thickness maps directly from 3D grids'

__version__ = _version.get_versions()['version']

xtg = XTGeoDialog()

XTGeoDialog.print_xtgeo_header(appname, __version__)


# -----------------------------------------------------------------------------
# Logging setup
# -----------------------------------------------------------------------------

format = xtg.loggingformat

logging.basicConfig(format=format, stream=sys.stdout)
logging.getLogger().setLevel(xtg.logginglevel)

logger = logging.getLogger(appname)

# -----------------------------------------------------------------------------
# Parse command line and YAML file
# -----------------------------------------------------------------------------


def do_parse_args(args):

    args = _configparser.parse_args(args, appname, appdescr)

    return args


def yamlconfig(inputfile, args):
    """Read from YAML file and modify/override"""
    config = _configparser.yconfig(inputfile)

    config = _configparser.yconfig_override(config, args, appname)

    config = _configparser.yconfig_set_defaults(config, appname)

    return config


def get_grid_props_data(config, appname):
    """Get the relevant Grid and props data."""

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

    # get the numpies
    initd, restartd = (
        _get_grid_props.get_numpies_hc_thickness(config, grd, initobjects,
                                                 restobjects, dates))

    # returns also dates since dates list may be updated after import
    return initd, restartd, dates


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
        A numpy zonation 3D array
    """
    zonation, zoned = _get_zonation_filters.zonation(config, dz)

    return zonation, zoned


def compute_hcpfz(config, initd, restartd, dates):

    hcpfzd = _compute_hcpfz.get_hcpfz(config, initd, restartd, dates)

    return hcpfzd


def formatnames(config, zname, date1, date2=None, option=None):
    """Format the names of the output to the form:

        zname--oilthickness--2011_01_01.*
        zname--oilthickness_diff--2011_01_01-2007_01_01.*

    The last is option which may have 'diff'
    """


def plotmap(config, initd, hcpfzd, zonation, zoned):

    mapzd = _plotmap.do_mapping(config, initd, hcpfzd, zonation, zoned)

    if config['output']['plotfolder'] is not None:
        _plotmap.do_plotting(config, mapzd)


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

    # import data from files and return releavnt numpies
    xtg.say('Import files...')
    initd, restartd, dates = (
        import_pdata(config, appname, gfile, initlist, restartlist, dates))

    # Get the zonations
    xtg.say('Get zonation info')
    zonation, zoned = get_zranges(config, initd['dz'])

    xtg.say('Compute HCPFZ property')
    hcpfzd = compute_hcpfz(config, initd, restartd, dates)

    xtg.say('Do mapping...')
    plotmap(config, initd, hcpfzd, zonation, zoned)


if __name__ == '__main__':
    main()
