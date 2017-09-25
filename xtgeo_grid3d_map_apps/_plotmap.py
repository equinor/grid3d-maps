# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import

import sys
import logging
import numpy as np

from xtgeo.common import XTGeoDialog
from xtgeo.surface import RegularSurface

xtg = XTGeoDialog()

# -----------------------------------------------------------------------------
# Logging setup
# -----------------------------------------------------------------------------

format = xtg.loggingformat

logging.basicConfig(format=format, stream=sys.stdout)
logging.getLogger().setLevel(xtg.logginglevel)

logger = logging.getLogger(__name__)


def do_mapping(config, initd, hcpfzd, zonation, zoned):
    """Do mapping"""

    # tmp until stuff works
    layerlist = (1, 999999)

    mapzd = dict()

    for zname, zrange in zoned.items():

        if zname == 'all':
            if config['computesettings']['all'] is not True:
                logger.info('Skip <{}> (cf. computesettings: all)'.
                            format(zname))
                continue
        else:
            if config['computesettings']['zone'] is not True:
                logger.info('Skip <{}> (cf. computesettings: zone)'.
                            format(zname))
                continue

        mapd = dict()
        for date, hcpfz in hcpfzd.items():

            xtg.say('Mapping <{}> for date <{}> ...'.format(zname, date))

            ncol = config['mapsettings'].get('ncol')
            nrow = config['mapsettings'].get('nrow')

            xmap = RegularSurface(
                xori=config['mapsettings'].get('xori'),
                yori=config['mapsettings'].get('yori'),
                nx=config['mapsettings'].get('ncol'),
                ny=config['mapsettings'].get('nrow'),
                xinc=config['mapsettings'].get('xinc'),
                yinc=config['mapsettings'].get('yinc'),
                values=np.zeros((ncol, nrow))
            )

            xmap.hc_thickness_from_3dprops(xprop=initd['xc'],
                                           yprop=initd['yc'],
                                           hcpfzprop=hcpfz,
                                           zoneprop=zonation,
                                           zone_minmax=tuple(zrange),
                                           layer_minmax=layerlist)

            filename = _mapsettings(config, zname, date)
            xmap.to_file(filename)

            mapd[date] = xmap

        mapzd[zname] = mapd

    # return the map dictionary: {zname: {date1: map_object1, ...}}

    return mapzd


def do_plotting(config, mapzd):
    """Do plotting via matplotlib to PNG (etc) (if requested)"""

    xtg.say('Plotting ...')
    for zname, mapd in mapzd.items():
        for date, xmap in mapd.items():
            plotfile = (config['output']['plotfolder'] + '/all' +
                        '--hcthickness--' + date + '.png')
            title = ('HC thickness for ' + date + ' ' +
                     config['computesettings']['mode'])

            mytxt = 'moho'
            xlabelrotation = 25
            valuerange = (None, None)
            coltable = 'rainbow'

            xmap.quickplot(filename=plotfile, title=title, infotext=mytxt,
                           xlabelrotation=xlabelrotation, minmax=valuerange,
                           colortable=coltable)



def _mapsettings(config, zname, date):
    """Local function for map name"""

    delim = '--'

    mapfilename = (config['output']['mapfolder'] + '/' + zname + delim +
                   'hcthickness' + delim + str(date) + '.gri')

    return mapfilename
