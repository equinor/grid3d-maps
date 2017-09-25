import os
import sys
import logging

from xtgeo.surface import RegularSurface
from xtgeo.common import XTGeoDialog

import xtgeo_grid3d_map_apps.xtgeo_grid3d_map_apps as xx

xtg = XTGeoDialog()

path = 'TMP'
try:
    os.makedirs(path)
except OSError:
    if not os.path.isdir(path):
        raise

# =============================================================================
# Do tests
# =============================================================================


def getlogger(name):

    format = '%(msecs)6.2f %(name)54s [%(funcName)20s()] %(levelname)8s:'\
             + '\t%(message)s'

    logging.basicConfig(format=format, stream=sys.stdout)
    logging.getLogger().setLevel(xtg.logginglevel)  # root logger!

    return logging.getLogger(name)


def test_hc001():
    logger = getlogger('test_hc001')

    xx.main(['--config', 'tests/yaml/001.yaml'])

    # now read in result and check avg value
    x = RegularSurface('TMP/gull_1985_10_01.gri')
    avg = float("{:4.3f}".format(float(x.values.mean())))
    logger.info("AVG is " + str(avg))
    assert avg == 3.649


def test_hc001new():
    logger = getlogger('test_hc001new')

    xx.main(['--config', 'tests/yaml/001_new.yaml'])

    # now read in result and check avg value
    x = RegularSurface('TMP/gull_1985_10_01.gri')
    avg = float("{:4.3f}".format(float(x.values.mean())))
    logger.info("AVG is " + str(avg))

    assert avg == 3.649


def test_hc002():
    logger = getlogger('test_hc002')

    xx.main(['--config', 'tests/yaml/002.yaml'])

    # now read in result and check avg value
    # x = RegularSurface('TMP/all--oilthickness--1985_10_01.gri')
    # avg = float("{:4.3f}".format(float(x.values.mean())))
    # logger.info("AVG is " + str(avg))

    # assert avg == 3.649


def test_hc003():
    """Gullfaks simple gas thickness"""
    logger = getlogger('test_hc003')

    xx.main(['--config', 'tests/yaml/003.yaml'])

    # now read in result and check avg value
    # x = RegularSurface('TMP/all--oilthickness--1985_10_01.gri')
    # avg = float("{:4.3f}".format(float(x.values.mean())))
    # logger.info("AVG is " + str(avg))

    # assert avg == 3.649


def test_hc004():
    """Gullfaks simple gas ROCK thickness for all ROCK"""
    logger = getlogger('test_hc004')

    xx.main(['--config', 'tests/yaml/004.yaml'])

    # now read in result and check avg value
    # x = RegularSurface('TMP/all--oilthickness--1985_10_01.gri')
    # avg = float("{:4.3f}".format(float(x.values.mean())))
    # logger.info("AVG is " + str(avg))

    # assert avg == 3.649
