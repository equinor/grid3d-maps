# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import

import pprint
from collections import defaultdict
import numpy.ma as ma

from xtgeo.common import XTGeoDialog
from xtgeo.grid3d import Grid
from xtgeo.grid3d import GridProperties
from xtgeo.grid3d import GridProperty

xtg = XTGeoDialog()

logger = xtg.functionlogger(__name__)


def files_to_import(config, appname):
    """Get a list of files to import, based on config"""

    folderroot = None
    if 'folderroot' in config['input']:
        if config['input']['folderroot'] is not None:
            folderroot = config['input']['folderroot']


    eclroot = None
    if 'eclroot' in config['input']:
        if config['input']['eclroot'] is not None:
            eclroot = config['input']['eclroot']

    gfile = ''
    initlist = dict()
    restartlist = dict()
    dates = []

    if eclroot:
        gfile = eclroot + '.EGRID'

    if 'grid' in config['input']:
        gfile = config['input']['grid']

    if appname == 'grid3d_hc_thickness':

        if 'xhcpv' in config['input']:
            initlist['xhcpv'] = config['input']['xhcpv']

        else:
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

        logger.debug(config['input'])

        for item in config['input']:
            if item == 'folderroot':
                continue
            if item == 'eclroot':
                continue
            elif item == 'grid':
                gfile = config['input']['grid']
                if '$folderroot' in gfile:
                    gfile = gfile.replace('$folderroot', folderroot)
                if '$eclroot' in gfile:
                    gfile = gfile.replace('$eclroot', eclroot)
            else:
                if 'UNRST' in config['input'][item]:
                    if '--' in item:
                        param = item.split('--')[0]
                        date = item.split('--')[1]

                    rfile = config['input'][item]
                    if '$folderroot' in rfile:
                        rfile = rfile.replace('$folderroot', folderroot)
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
                    if '$folderroot' in ifile:
                        ifile = ifile.replace('$folderroot', folderroot)
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

    Args:
        config(dict): Th configuration dictionary
        appname(str): Name of application

    """

    logger.info('Import data for {}'.format(appname))

    # get the grid data + some geometrics
    grd = Grid(gfile, fformat='guess')

    # collect data per initfile etc: make a dict on the form:
    # {initfilename: [[prop1, lookfor1], [prop2, lookfor2], ...]} the
    # trick is defaultdict!
    #
    # The initfile itself may be a file or dictionary itself, e.g. either
    # SOME.INIT or {Name: somefile.roff}. In the latter, we should look for
    # Name in the file while doing the import.

    initdict = defaultdict(list)
    for ipar, ifile in initlist.items():
        logger.info('Parameter INIT: {} \t file is {}'.format(ipar, ifile))
        if isinstance(ifile, dict):
            print(repr(ifile))
            lookfor, usefile = list(ifile.keys()), list(ifile.values())
            initdict[usefile[0]].append([ipar, lookfor[0]])
        else:
            lookfor = ipar

            # if just a name: file.roff, than the name here and name in
            # the file may not match. So here it is assumed that "lookfor"
            # shall be 'unknown'

            if ifile.endswith('.roff'):
                lookfor = 'unknown'

            initdict[ifile].append([ipar, lookfor])

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
        if len(iniprops) > 1:
            tmp = GridProperties()
            lookfornames = []
            usenames = []
            for iniprop in iniprops:
                usename, lookforname = iniprop
                lookfornames.append(lookforname)
                usenames.append(usename)

            tmp.from_file(inifile, names=lookfornames,
                          fformat='init', grid=grd)
            for i, name in enumerate(lookfornames):
                prop = tmp.get_prop_by_name(name)
                prop.name = usenames[i]  # rename if different
                initobjects.append(prop)

        else:
            # single properties, typically ROFF stuff
            tmp = GridProperty()
            usename, lookforname = iniprops[0]

            tmp.from_file(inifile, name=lookforname, fformat='guess',
                          grid=grd)
            tmp.name = usename
            initobjects.append(tmp)

    # restarts; will issue an warning if one or more dates are not found
    # assume that this is Eclipse stuff .UNRST
    restobjects = []
    for restfile, restprops in restdict.items():
        tmp = GridProperties()
        try:
            logger.info('Reading--')
            tmp.from_file(restfile, names=restprops,
                          fformat='unrst', grid=grd, dates=dates)

        except RuntimeWarning as rwarn:
            logger.info('Got warning...')
            xtg.warn(rwarn)
            for prop in tmp.props:
                logger.info('Append prop: {}'.format(prop))
                restobjects.append(prop)
        except Exception as message:
            raise SystemExit(message)
        else:
            logger.info('Works further...')
            for prop in tmp.props:
                logger.info('Append prop: {}'.format(prop))
                restobjects.append(prop)

    newdateslist = []
    for rest in restobjects:
        newdateslist.append(rest.date)

    newdateslist = list(set(newdateslist))
    logger.info('Actual dates to use: {}'.format(newdateslist))

    for obj in initobjects:
        logger.info('Init object for <{}> is <{}> '.format(obj.name, obj))

    for obj in restobjects:
        logger.info('Restart object for <{}> is <{}> '.format(obj.name, obj))

    return grd, initobjects, restobjects, newdateslist


def get_numpies_hc_thickness(config, grd, initobjects, restobjects, dates):
    """Process for HC thickness map; to get the needed numpies"""

    actnum = grd.get_actnum().values3d
    # mask is False  to get values for all cells, also inactive
    xc, yc, zc = grd.get_xyz(mask=False)
    xc = xc.values3d
    yc = yc.values3d
    zc = zc.values3d

    dz = grd.get_dz(mask=False).values3d
    dz[actnum == 0] = 0.0

    dx, dy = grd.get_dxdy()
    dx = dx.values3d
    dy = dy.values3d

    initd = {'iactnum': actnum, 'xc': xc, 'yc': yc, 'zc': zc, 'dx': dx,
             'dy': dy, 'dz': dz}

    if config['computesettings']['critmode']:
        crname = config['computesettings']['critmode'].upper()
    else:
        crname = None

    xmethod = config['computesettings']['method']
    xinput = config['input']

    if 'xhcpv' in xinput:
        xhcpv = initobjects[0].values3d
        xhcpv[actnum == 0] = 0.0
        initd.update({'xhcpv': xhcpv})

    else:

        if xmethod == 'use_poro' or xmethod == 'use_porv':
            # initobjects is a list of GridProperty objects (single)
            for prop in initobjects:
                if prop.name == 'PORO':
                    poro = prop.values3d
                if prop.name == 'NTG':
                    ntg = prop.values3d
                if prop.name == 'PORV':
                    porv = prop.values3d
                if prop.name == 'DX':
                    dx = prop.values3d
                if prop.name == 'DY':
                    dy = prop.values3d
                if prop.name == 'DZ':
                    dz = prop.values3d
                if crname is not None and prop.name == crname:
                    soxcr = prop.values3d

            porv[actnum == 0] = 0.0
            poro[actnum == 0] = 0.0
            ntg[actnum == 0] = 0.0
            dz[actnum == 0] = 0.0

            initd.update({'porv': porv, 'poro': poro, 'ntg': ntg, 'dx': dx,
                          'dy': dy, 'dz': dz})

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
        nsoil = 0
        for prop in restobjects:
            pname = 'SWAT' + '_' + str(date)
            if prop.name == pname:
                swat[date] = prop.values3d
                nsoil += 1

            pname = 'SGAS' + '_' + str(date)
            if prop.name == pname:
                sgas[date] = prop.values3d
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

    for prop in initobjects:
        logger.debug('INIT PROP name {}'.format(prop.name))

    for prop in restobjects:
        logger.debug('REST PROP name {}'.format(prop.name))

    propd = {}

    for pname in config['input']:
        usepname = pname
        if pname in set(['folderroot', 'eclroot', 'grid']):
            continue

        # initdata may also contain date if ROFF is input!
        if '--' in pname:
            name = pname.split('--')[0]
            date = pname.split('--')[1]

            # treating difference values
            if '-' in date:
                date1 = date.split('-')[0]
                date2 = date.split('-')[1]

                usepname1 = name + '_' + date1
                usepname2 = name + '_' + date2

                ok1 = False
                ok2 = False

                for prop in initobjects + restobjects:
                    if usepname1 == prop.name:
                        ptmp1 = prop.values3d
                        ok1 = True
                    if usepname2 == prop.name:
                        ptmp2 = prop.values3d
                        ok2 = True

                    if ok1 and ok2:
                        ptmp = ptmp1 - ptmp2
                        propd[pname] = ptmp
                        logger.debug('DIFF were made: {}'.format(pname))

            # only one date
            else:
                for prop in initobjects + restobjects:
                    usepname = pname.replace('--', '_')
                    if usepname == prop.name:
                        ptmp = prop.values3d
                        propd[pname] = ptmp

        # no dates
        else:
            for prop in initobjects + restobjects:
                if usepname == prop.name:
                    ptmp = prop.values3d
                    propd[pname] = ptmp

    logger.info('Return specd from {} is {}'.format(__name__, specd.keys()))
    logger.info('Return propd from {} is {}'.format(__name__, propd.keys()))
    return specd, propd
