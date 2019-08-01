# -*- coding: utf-8 -*-
try:
    from ._theversion import version
    __version__ = version
except ImportError:
    __version__ = "0.0.0"
