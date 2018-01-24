# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import

import pprint

from xtgeo.common import XTGeoDialog

xtg = XTGeoDialog()

logger = xtg.functionlogger(__name__)


def get_hcpfz(config, initd, restartd, dates, hcmode):
    """Compute a dictionary with hcpfz numpy (per date)."""
    # There may be cases where dates are missing, e.g. if computing
    # directly from the stoiip parameter.

    hcpfzd = dict()

    # use the given date from config if stoiip, giip, etc as info
    gdate = config['input']['dates'][0]

    if 'xhcpv' in config['input']:
        area = initd['dx'] * initd['dy']
        hcpfzd[gdate] = initd['xhcpv'] / area

    else:
        hcpfzd = _get_hcpfz_ecl(config, initd, restartd, dates, hcmode)

    alldates = hcpfzd.keys()

    ppalldates = pprint.PrettyPrinter(indent=4)
    logger.debug('After cleaning: {}'.format(ppalldates.pformat(alldates)))

    return hcpfzd


def _get_hcpfz_ecl(config, initd, restartd, dates, hcmode):
    # local function, get data from Eclipse INIT and RESTART

    hcpfzd = dict()

    shcintv = config['computesettings']['shc_interval']
    hcmethod = config['computesettings']['method']

    if not dates:
        xtg.error('Dates are missing. Bug?')
        raise RuntimeError('Dates er missing. Bug?')

    for date in dates:

        if hcmode == 'oil' or hcmode == 'gas':
            usehc = restartd['s' + hcmode + '_' + str(date)]
        elif hcmode == 'comb':
            usehc1 = restartd['s' + 'oil' + '_' + str(date)]
            usehc2 = restartd['s' + 'gas' + '_' + str(date)]
            usehc = usehc1 + usehc2
        else:
            raise ValueError('Invalid mode "{}" in "computesettings: method"'
                             .format(hcmode))

        if hcmethod == 'use_poro':
            usehc[usehc < shcintv[0]] = 0.0
            usehc[usehc > shcintv[1]] = 0.0
            hcpfzd[date] = initd['poro'] * initd['ntg'] * usehc * initd['dz']

        elif hcmethod == 'use_porv':
            area = initd['dx'] * initd['dy']
            usehc[usehc < shcintv[0]] = 0.0
            usehc[usehc > shcintv[1]] = 0.0
            hcpfzd[date] = initd['porv'] * usehc / area

        elif hcmethod == 'dz_only':
            usedz = initd['dz'].copy()
            usedz[usehc < shcintv[0]] = 0.0
            usedz[usehc > shcintv[1]] = 0.0
            hcpfzd[date] = usedz

        else:
            raise ValueError('Unsupported method "{}" in "computesettings:'
                             ' method"'.format(hcmethod))

        logger.info('HCPFZ minimum is {}'.format(hcpfzd[date].min()))
        logger.info('HCPFZ maximum is {}'.format(hcpfzd[date].max()))
        logger.debug('HCPFZ REPR is {}'.format(repr(hcpfzd[date])))

    for key, val in hcpfzd.items():
        logger.info('{}   {}'.format(key, type(val)))

    # An important issue here is that one may ask for difference dates,
    # not just dates. Hence need to iterate over the dates in the input
    # config and select the right one, and delete those that are not
    # relevant; e.g. one may ask for 20050816--19930101 but not for
    # 20050816; in that case the difference must be computed but
    # after that the 20050816 entry will be removed fomr the list

    cdates = config['input']['dates']

    for cdate in cdates:
        cdate = str(cdate)
        logger.debug('cdate is: '.format(cdate))
        if '-' in cdate:
            d1 = str(cdate.split('-')[0])
            d2 = str(cdate.split('-')[1])
            hcpfzd[cdate] = hcpfzd[d1] - hcpfzd[d2]

    alldates = hcpfzd.keys()

    ppalldates = pprint.PrettyPrinter(indent=4)
    logger.debug('All dates: {}'.format(ppalldates.pformat(alldates)))

    purecdates = [str(cda) for cda in cdates if '--' not in str(cda)]
    pureadates = [str(adate) for adate in alldates
                  if '--' not in str(adate)]

    for udate in pureadates:
        if udate not in purecdates:
            del hcpfzd[udate]

    return hcpfzd
