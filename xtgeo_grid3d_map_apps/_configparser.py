# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import

import argparse
import sys
import os.path
import yaml
import pprint
import copy

import logging

from xtgeo.common import XTGeoDialog

xtg = XTGeoDialog()

# -----------------------------------------------------------------------------
# Logging setup
# -----------------------------------------------------------------------------

format = xtg.loggingformat

logging.basicConfig(format=format, stream=sys.stdout)
logging.getLogger().setLevel(xtg.logginglevel)

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Parse command line
# -----------------------------------------------------------------------------


def parse_args(args, appname, appdescr):

    if args is None:
        args = sys.argv[1:]
    else:
        args = args

    usetxt = appname + ' --config some.yaml ... '

    parser = argparse.ArgumentParser(
        description=appdescr,
        usage=usetxt
    )

    parser.add_argument('-c', '--config',
                        dest='config',
                        type=str,
                        required=True,
                        help='Config file on YAML format (required)')

    parser.add_argument('-e', '--eclroot',
                        dest='eclroot',
                        type=str,
                        help='Eclipse root name')

    parser.add_argument('--mapfolder',
                        dest='mapfolder',
                        type=str,
                        help='Name of map output root')

    parser.add_argument('--plotfile',
                        dest='plotfolder',
                        type=str,
                        default=None,
                        help='Name of plot output root')

    parser.add_argument('-z', '--zname',
                        dest='zname',
                        type=str,
                        default='',
                        help='A zone name or description')

    parser.add_argument('--zfile',
                        dest='zfile',
                        type=str,
                        help='Explicit file (YAML) for zonation')

    if appname == 'grid3d_hc_thickness':

        parser.add_argument('-d', '--dates',
                            dest='dates',
                            nargs='+',
                            type=int,
                            default=None,
                            help='A list of dates on YYYYMMDD format')

        logger.debug('DATES')
        parser.add_argument('-m', '--mode',
                            dest='mode',
                            type=str,
                            default=None,
                            help='oil, gas or comb')

    if len(args) < 2:
        parser.print_help()
        print('QUIT')
        sys.exit(0)

    args = parser.parse_args(args)

    logger.debug('Command line args: ')
    for arg in vars(args):
        logger.debug('{}  {}'.format(arg, getattr(args, arg)))

    return args

# =============================================================================
# Read YAML input file
# Note if both config and other command line options, the present
# command line option will win over the config setting. This makes the
# system quite flexible.
# =============================================================================


def yconfig(inputfile):
    """Read from YAML file."""

    if not os.path.isfile(inputfile):
        logger.critical(
            'STOP! No such config file exists: {}'.format(inputfile))
        sys.exit(1)

    with open(inputfile, 'r') as stream:
        config = yaml.load(stream)

    xtg.say('')
    xtg.say('Input config YAML file <{}> is read...'.format(inputfile))

    pp = pprint.PrettyPrinter(indent=4)

    out = pp.pformat(config)
    logger.debug('\n{}'.format(out))

    return config


def yconfig_override(config, args, appname):
    """Override the YAML config with command line options"""

    newconfig = copy.deepcopy(config)

    if appname == 'grid3d_hc_thickness':

        if args.dates:
            newconfig['input']['dates'] = args.dates
            logger.debug('YAML config overruled by cmd line: dates are now {}'.
                         format(newconfig['eclinput']['dates']))

        if args.eclroot:
            newconfig['input']['eclroot'] = args.eclroot
            xtg.say('YAML config overruled... eclroot is now: <{}>'.
                    format(newconfig['input']['eclroot']))

    pp = pprint.PrettyPrinter(indent=4)
    out = pp.pformat(newconfig)
    logger.debug('After override: \n{}'.format(out))

    return newconfig


def yconfig_set_defaults(config, appname):
    """Override the YAML config with defaults where missing input."""

    newconfig = copy.deepcopy(config)

    # some defaults if data is missing...
    if 'title' not in newconfig:
        newconfig['title'] = 'SomeField'

    if 'mapfile' not in newconfig['output']:
        newconfig['output']['mapfile'] = 'hc_thickness'

    if 'plotfile' not in newconfig['output']:
        newconfig['output']['plotfile'] = None

    if 'mapfolder' not in newconfig['output']:
        newconfig['output']['mapfolder'] = '/tmp'

    if 'plotfolder' not in newconfig['output']:
        newconfig['output']['plotfolder'] = None

    if 'lowercase' not in newconfig['output']:
        newconfig['output']['lowercase'] = True

    if 'zname' not in newconfig['zonation']:
        newconfig['zonation']['zname'] = 'all'

    if 'yamlfile' not in newconfig['zonation']:
        newconfig['zonation']['yamlfile'] = None

    if appname == 'grid3d_hc_thickness':

        if 'mode' not in newconfig['computesettings']:
            newconfig['computesettings']['mode'] = 'oil'

        if 'method' not in newconfig['computesettings']:
            newconfig['computesettings']['method'] = 'use_poro'

        if 'shc_interval' not in newconfig['computesettings']:
            newconfig['computesettings']['shc_interval'] = [0.0001, 1.0]

        if 'critmode' not in newconfig['computesettings']:
            newconfig['computesettings']['critmode'] = None

        if newconfig['computesettings']['critmode'] is False:
            newconfig['computesettings']['critmode'] = None

        if 'zone' not in newconfig['computesettings']:
            newconfig['computesettings']['zone'] = False

        if 'all' not in newconfig['computesettings']:
            newconfig['computesettings']['all'] = True

    pp = pprint.PrettyPrinter(indent=4)
    out = pp.pformat(newconfig)
    logger.debug('After setting defaults: \n{}'.format(out))

    return newconfig


def yconfig_addons(config, appname):
    """Addons e.g. YAML import spesified in the top config."""

    newconfig = copy.deepcopy(config)

    if config['zonation']['yamlfile'] is not None:

        # re-use yconfig:
        zconfig = yconfig(config['zonation']['yamlfile'])
        if 'zranges' in zconfig:
            newconfig['zonation']['zranges'] = zconfig['zranges']

    return newconfig
