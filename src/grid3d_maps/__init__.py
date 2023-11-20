"""Top-level package for grid3d_maps"""

try:
    from ._theversion import version

    __version__ = version
except ImportError:
    __version__ = "0.0.0"
