# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import

import sys
import pprint
from collections import defaultdict
import numpy.ma as ma

from xtgeo.common import XTGeoDialog
from xtgeo.grid3d import Grid
from xtgeo.grid3d import GridProperties

xtg = XTGeoDialog()

logger = xtg.functionlogger(__name__)


def files_to_import(config, appname):
    """Get a list of files to import, based on config"""

    eclroot = None
    if 'eclroot' in config['input']:
        if config['input']['eclroot'] is not None:
            eclroot = config['input']['eclroot']

    gfile = ''
    initlist = dict()
    restartlist = dict()
    dates = []

    if appname == 'grid3d_hc_thickness':
        gfile = eclroot + '.EGRID'
        initlist['PORO'] = eclroot + '.INIT'
        initlist['NTG'] = eclroot + '.INIT'
        initlist['PORV'] = eclroot + '.INIT'
        initlist['DX'] = eclroot + '.INIT'
        initlist['DY'] = eclroot + '.INIT'
        initlist['DZ'] = eclroot + '.INIT'
        if config['computesettings']['critmode']:
            crname = config['computesettings']['critmode'].upper()
            initlist[crname] = eclroot + '.INIT'

        restartlist['SWAT'] = eclroot + '.UNRST'
        restartlist['SGAS'] = eclroot + '.UNRST'

        for date in config['input']['dates']:
            logger.debug('DATE {}'.format(date))
            if len(date) == 8:
                dates.append(date)
            elif len(date) > 12:
                dates.append(date.split('-')[0])
                dates.append(date.split('-')[1])

    if appname == 'grid3d_average_map':

        # Put things in initlist or restart list. Only Eclipse
        # UNRST comes in the restartlist, all other in the initlist.
        # For instance, a ROFF parameter PRESSURE_20110101 will
        # technically be an initlist parameter here

        gfile = eclroot + '.EGRID'  # default, if 'grid' is missing

        logger.debug(config['input'])

        for item in config['input']:
            if item == 'eclroot':
                continue
            elif item == 'grid':
                gfile = config['input']['grid']
                if '$eclroot' in gfile:
                    gfile = gfile.replace('$eclroot', eclroot)
            else:
                if 'UNRST' in config['input'][item]:
                    if '--' in item:
                        param = item.split('--')[0]
                        date = item.split('--')[1]

                    rfile = config['input'][item]
                    if '$eclroot' in rfile:
                        rfile = rfile.replace('$eclroot', eclroot)
                    restartlist[param] = rfile
                    # dates:
                    if len(date) > 10:
                        dates.append(date.split('-')[0])
                        dates.append(date.split('-')[1])
                    else:
                        dates.append(date)

                else:
                    ifile = config['input'][item]
                    if '$eclroot' in ifile:
                        ifile = ifile.replace('$eclroot', eclroot)
                    initlist[item] = ifile

        logger.debug(dates)

    dates = list(sorted(set(dates)))  # to get a list with unique dates

    ppinit = pprint.PrettyPrinter(indent=4)
    pprestart = pprint.PrettyPrinter(indent=4)
    ppdates = pprint.PrettyPrinter(indent=4)

    logger.debug('Grid from {}'.format(gfile))
    logger.debug('{}'.format(ppinit.pformat(initlist)))
    logger.debug('{}'.format(pprestart.pformat(restartlist)))
    logger.debug('{}'.format(ppdates.pformat(dates)))

    return gfile, initlist, restartlist, dates


def import_data(config, appname, gfile, initlist,
                restartlist, dates):
    """Get the grid and the props data.

    Well get the grid and the propsdata for data to be plotted,
    zonation (if required), filters (if required)

    Will return data on appropriate format...
    """

    logger.info('Import data for {}'.format(appname))

    # get the grid data + some geometrics
    grd = Grid(gfile, fformat='egrid')

    # collect data per initfile etc: make a dict on the form:
    # {initfilename: [prop1, prop2, ...]} trick is defaultdict!
    initdict = defaultdict(list)
    for ipar, ifile in initlist.items():
        logger.info('Parameter INIT: {} \t file is {}'.format(ipar, ifile))
        initdict[ifile].append(ipar)

    ppinitdict = pprint.PrettyPrinter(indent=4)
    logger.debug('\n{}'.format(ppinitdict.pformat(initdict)))

    restdict = defaultdict(list)
    for rpar, rfile in restartlist.items():
        logger.info('Parameter RESTART: {} \t file is {}'.format(rpar, rfile))
        restdict[rfile].append(rpar)

    pprestdict = pprint.PrettyPrinter(indent=4)
    logger.debug('\n{}'.format(pprestdict.pformat(restdict)))

    initobjects = []
    for inifile, iniprops in initdict.items():
        tmp = GridProperties()
        tmp.from_file(inifile, names=iniprops,
                      fformat='init', grid=grd)
        initobjects.append(tmp)

    # restarts; will issue an warning if one or more dates are not found
    restobjects = []
    for restfile, restprops in restdict.items():
        tmp = GridProperties()
        try:
            tmp.from_file(restfile, names=restprops,
                          fformat='unrst', grid=grd, dates=dates)

        except RuntimeWarning as rwarn:
            xtg.warn(rwarn)
            restobjects.append(tmp)
        except Exception:
            sys.exit(22)
        else:
            restobjects.append(tmp)

    newdateslist = []
    for rest in restobjects:
        newdateslist += rest.dates

    logger.debug('Actual dates to use: {}'.format(newdateslist))

    return grd, initobjects, restobjects, newdateslist


def get_numpies_hc_thickness(config, grd, initobjects, restobjects, dates):
    """Process for HC thickness map; to get the needed numpies"""

    actnum = grd.get_actnum().values3d
    # mask is False  to get values for all cells, also inactive
    xc, yc, zc = grd.get_xyz(mask=False)
    xc = xc.values3d
    yc = yc.values3d
    zc = zc.values3d

    if config['computesettings']['critmode']:
        crname = config['computesettings']['critmode'].upper()
    else:
        crname = None

    for props in initobjects:
        if 'PORO' in props.names:
            poro = props.get_prop_by_name('PORO').values3d
        if 'NTG' in props.names:
            ntg = props.get_prop_by_name('NTG').values3d
        if 'PORV' in props.names:
            porv = props.get_prop_by_name('PORV').values3d
        if 'DX' in props.names:
            dx = props.get_prop_by_name('DX').values3d
        if 'DX' in props.names:
            dy = props.get_prop_by_name('DY').values3d
        if 'DZ' in props.names:
            dz = props.get_prop_by_name('DZ').values3d
        if crname is not None and crname in props.names:
            soxcr = props.get_prop_by_name(crname).values3d

    porv[actnum == 0] = 0.0
    poro[actnum == 0] = 0.0
    ntg[actnum == 0] = 0.0
    dz[actnum == 0] = 0.0

    initd = {'porv': porv, 'poro': poro, 'ntg': ntg, 'dx': dx, 'dy': dy,
             'dz': dz, 'xc': xc, 'yc': yc, 'zc': zc}

    if crname is not None:
        initd['soxcr'] = soxcr
    else:
        initd['soxcr'] = None

    xtg.say('Got relevant INIT numpies, OK ...')

    # restart data, they have alos a date component:

    restartd = {}

    sgas = dict()
    swat = dict()
    soil = dict()

    for date in dates:
        for props in restobjects:
            nsoil = 0
            pname = 'SWAT' + '_' + str(date)
            if pname in props.names:
                swat[date] = props.get_prop_by_name(pname).values3d
                nsoil += 1

            pname = 'SGAS' + '_' + str(date)
            if pname in props.names:
                sgas[date] = props.get_prop_by_name(pname).values3d
                nsoil += 1

            if nsoil == 2:
                soil[date] = ma.ones(sgas[date].shape, dtype=sgas[date].dtype)
                soil[date] = soil[date] - swat[date] - sgas[date]

                if crname is not None:
                    soil[date] = soil[date] - soxcr

        logger.debug('Date is {} and  SWAT is {}'.format(date, swat))
        logger.debug('Date is {} and  SGAS is {}'.format(date, sgas))
        logger.debug('Date is {} and  SOIL is {}'.format(date, soil))

        # numpy operations on the saturations
        for anp in [soil[date], sgas[date]]:
            anp[anp > 1.0] = 1.0
            anp[anp < 0.0] = 0.0
            anp[actnum == 0] = 0.0

        restartd['sgas_' + str(date)] = sgas[date]
        restartd['swat_' + str(date)] = swat[date]
        restartd['soil_' + str(date)] = soil[date]

    for key in initd:
        logger.debug('INITS: Key and object {} {}'
                     .format(key, type(initd[key])))

    for key in restartd:
        logger.debug('RESTARTS: Key and object {} {}'
                     .format(key, type(restartd[key])))

    return initd, restartd


def get_numpies_avgprops(config, grd, initobjects, restobjects, dates):
    """Process for average map; to get the needed numpies"""

    actnum = grd.get_actnum().values3d
    # mask is False  to get values for all cells, also inactive
    xc, yc, zc = grd.get_xyz(mask=False)
    xc = xc.values3d
    yc = yc.values3d
    zc = zc.values3d
    dz = grd.get_dz(mask=False).values3d

    dz[actnum == 0] = 0.0

    # store these in a dict for special data (specd):
    specd = {'idz': dz, 'ixc': xc, 'iyc': yc, 'izc': zc, 'iactnum': actnum}

    for props in initobjects:
        for n in props.names:
            logger.debug('INIT PROP name {}'.format(n))

    for props in restobjects:
        for n in props.names:
            logger.debug('REST PROP name {}'.format(n))

    propd = {}
    for props in initobjects + restobjects:

        for pname in config['input']:
            usepname = pname
            if pname == 'eclroot' or pname == 'grid':
                continue

            # initdata may also contain date if ROFF is input!
            if '--' in pname:
                prop = pname.split('--')[0]
                date = pname.split('--')[1]

                # treating difference values
                if '-' in date:
                    date1 = date.split('-')[0]
                    date2 = date.split('-')[1]

                    usepname1 = prop + '_' + date1
                    usepname2 = prop + '_' + date2

                    ok1 = False
                    ok2 = False

                    if usepname1 in props.names:
                        ptmp1 = props.get_prop_by_name(usepname1).values3d
                        ok1 = True
                    if usepname2 in props.names:
                        ptmp2 = props.get_prop_by_name(usepname2).values3d
                        ok2 = True

                    if ok1 and ok2:
                        ptmp = ptmp1 - ptmp2
                        propd[pname] = ptmp

                # only one date
                else:
                    usepname = pname.replace('--', '_')
                    if usepname in props.names:
                        ptmp = props.get_prop_by_name(usepname).values3d
                        propd[pname] = ptmp

            # no dates
            else:
                if usepname in props.names:
                    ptmp = props.get_prop_by_name(usepname).values3d
                    propd[pname] = ptmp

    logger.info('Return specd from {} is {}'.format(__name__, specd.keys()))
    logger.info('Return propd from {} is {}'.format(__name__, propd.keys()))
    return specd, propd
