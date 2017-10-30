# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import

import sys
import pprint
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


def get_hcpfz(config, initd, restartd, dates):
    """Compute a dictionary with hcpfz numpy per date"""

    hcpfzd = dict()

    shcintv = config['computesettings']['shc_interval']

    if not dates:
        xtg.error('Dates er missing. Bug?')
        raise RuntimeError('Dates er missing. Bug?')

    for date in dates:

        usehc = restartd['s' + config['computesettings']['mode'] + '_' +
                         str(date)]

        if config['computesettings']['method'] == 'use_poro':
            usehc[usehc < shcintv[0]] = 0.0
            usehc[usehc > shcintv[1]] = 0.0
            hcpfzd[date] = initd['poro'] * initd['ntg'] * usehc * initd['dz']

        elif config['computesettings']['method'] == 'use_porv':
            area = initd['dx'] * initd['dy']
            usehc[usehc < shcintv[0]] = 0.0
            usehc[usehc > shcintv[1]] = 0.0
            hcpfzd[date] = initd['porv'] * usehc / area

        elif config['computesettings']['method'] == 'dz_only':
            usedz = initd['dz'].copy()
            usedz[usehc < shcintv[0]] = 0.0
            usedz[usehc > shcintv[1]] = 0.0
            hcpfzd[date] = usedz

        else:
            raise RuntimeError('Unsupported computesettings: method')

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
    pureadates = [str(adate) for adate in alldates if '--' not in str(adate)]

    for udate in pureadates:
        if udate not in purecdates:
            del hcpfzd[udate]

    alldates = hcpfzd.keys()

    logger.debug('After cleaning: {}'.format(ppalldates.pformat(alldates)))

    return hcpfzd
