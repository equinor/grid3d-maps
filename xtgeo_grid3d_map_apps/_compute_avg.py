# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import

import getpass
from time import localtime, strftime
import numpy as np
from collections import OrderedDict

from xtgeo.common import XTGeoDialog
from xtgeo.surface import RegularSurface
from xtgeo.xyz import Polygons

xtg = XTGeoDialog()
logger = xtg.functionlogger(__name__)


def get_avg(config, specd, propd, dates, zonation, zoned):
    """Compute a dictionary with average numpy per date

    It will return a dictionary per parameter and eventually dates"""

    avgd = OrderedDict()

    ncol = config['mapsettings'].get('ncol')
    nrow = config['mapsettings'].get('nrow')

    xmap = RegularSurface(xori=config['mapsettings'].get('xori'),
                          yori=config['mapsettings'].get('yori'),
                          ncol=ncol,
                          nrow=nrow,
                          xinc=config['mapsettings'].get('xinc'),
                          yinc=config['mapsettings'].get('yinc'),
                          values=np.zeros((ncol, nrow)))

    xtg.say('Mapping ...')

    for zname, zrange in zoned.items():

        logger.info('ZNAME and ZRANGE are {}:  {}'.format(zname, zrange))
        usezonation = zonation
        usezrange = zrange

        # in case of super zones:
        if isinstance(zrange, list):
            usezonation = zonation.copy()
            usezonation[:, :, :] = 0
            logger.debug(usezonation)
            for zr in zrange:
                logger.info('ZR is {}'.format(zr))
                usezonation[zonation == zr] = 888

            usezrange = 888

        if zname == 'all':
            usezonation = zonation.copy()
            usezonation[:, :, :] = 999
            usezrange = 999

            if config['computesettings']['all'] is not True:
                logger.info('Skip <{}> (cf. computesettings: all)'.
                            format(zname))
                continue
        else:
            if config['computesettings']['zone'] is not True:
                logger.info('Skip <{}> (cf. computesettings: zone)'.
                            format(zname))
                continue

        for propname, pvalues in propd.items():

            xmap.avg_from_3dprop(xprop=specd['ixc'],
                                 yprop=specd['iyc'],
                                 mprop=pvalues,
                                 dzprop=specd['idz'],
                                 zoneprop=usezonation,
                                 zone_minmax=[usezrange, usezrange])

            filename = _avg_filesettings(config, zname, propname, mode='map')
            usename = (zname, propname)

            avgd[usename] = xmap.copy()

            xtg.say('Map file to {}'.format(filename))
            avgd[usename].to_file(filename)

    return avgd


def do_avg_plotting(config, avgd):
    """Do plotting via matplotlib to PNG (etc) (if requested)"""

    xtg.say('Plotting ...')

    for names, xmap in avgd.items():

        # 'names' is a tuple as (zname, pname)
        zname = names[0]
        pname = names[1]

        plotfile = _avg_filesettings(config, zname, pname, mode='plot')

        pcfg = _avg_plotsettings(config, zname, pname)

        xtg.say('Plot to {}'.format(plotfile))

        usevrange = pcfg['valuerange']

        faults = None
        if pcfg['faultpolygons'] is not None:
            xtg.say('Try: {}'.format(pcfg['faultpolygons']))
            try:
                fau = Polygons(pcfg['faultpolygons'], fformat='zmap')
                faults = {'faults': fau}
                xtg.say('Use fault polygons')
            except Exception as e:
                xtg.say(e)
                faults = None
                xtg.say('No fault polygons')

        xmap.quickplot(filename=plotfile,
                       title=pcfg['title'],
                       infotext=pcfg['infotext'],
                       xlabelrotation=pcfg['xlabelrotation'],
                       minmax=usevrange,
                       colortable=pcfg['colortable'],
                       faults=faults)


def _avg_filesettings(config, zname, pname, mode='root'):
    """Local function for map or plot file root name"""

    delim = '--'

    if config['output']['lowercase']:
        zname = zname.lower()
        pname = pname.lower()

    if config['output']['tag']:
        tag = config['output']['tag'] + '_'
    else:
        tag = ''

    xfil = zname + delim + tag + 'average' + '_' + pname

    if mode == 'root':
        return xfil

    elif mode == 'map':
        path = config['output']['mapfolder'] + '/'
        xfil = xfil + '.gri'

    elif mode == 'plot':
        path = config['output']['plotfolder'] + '/'
        xfil = xfil + '.png'

    return path + xfil


def _avg_plotsettings(config, zname, pname):
    """Local function for plot additional info for AVG maps."""

    title = 'Weighted average for ' + pname + ', zone ' + zname

    showtime = strftime("%Y-%m-%d %H:%M:%S", localtime())
    infotext = getpass.getuser() + ' ' + showtime
    if config['output']['tag']:
        infotext = infotext + ' (tag: ' + config['output']['tag'] + ')'

    xlabelrotation = None
    valuerange = (None, None)
    diffvaluerange = (None, None)
    colortable = 'rainbow'
    xlabelrotation = 0
    fpolyfile = None

    if 'xlabelrotation' in config['plotsettings']:
        xlabelrotation = config['plotsettings']['xlabelrotation']

    if 'valuerange' in config['plotsettings']:
        valuerange = tuple(config['plotsettings']['valuerange'])

    if 'diffvaluerange' in config['plotsettings']:
        diffvaluerange = tuple(config['plotsettings']['diffvaluerange'])

    if 'faultpolygons' in config['plotsettings']:
        fpolyfile = config['plotsettings']['faultpolygons']

    # there may be individual plotsettings for zname
    if zname is not None and zname in config['plotsettings']:

        zfg = config['plotsettings'][zname]

        if 'valuerange' in zfg:
            valuerange = tuple(zfg['valuerange'])

        if 'diffvaluerange' in zfg:
            diffvaluerange = tuple(zfg['diffvaluerange'])

        if 'xlabelrotation' in zfg:
            xlabelrotation = zfg['xlabelrotation']

        if 'colortable' in zfg:
            colortable = zfg['colortable']

        if 'faultpolygons' in zfg:
            fpolyfile = zfg['faultpolygons']

    # assing settings to a dictionary which is returned
    plotcfg = {}
    plotcfg['title'] = title
    plotcfg['infotext'] = infotext
    plotcfg['valuerange'] = valuerange
    plotcfg['diffvaluerange'] = diffvaluerange
    plotcfg['xlabelrotation'] = xlabelrotation
    plotcfg['colortable'] = colortable
    plotcfg['faultpolygons'] = fpolyfile

    return plotcfg
