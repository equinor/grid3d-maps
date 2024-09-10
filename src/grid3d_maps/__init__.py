"""Top-level package for grid3d_maps"""

import logging
import sys

try:
    from .version import __version__

except ImportError:
    __version__ = "0.0.0"

logger = logging.getLogger(__name__)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
std_out_handler = logging.StreamHandler(sys.stdout)
std_out_handler.setFormatter(formatter)
std_out_handler.setLevel(logging.INFO)
logger.addHandler(std_out_handler)

std_err_handler = logging.StreamHandler(sys.stderr)
std_err_handler.setFormatter(formatter)
std_err_handler.setLevel(logging.WARNING)
logger.addHandler(std_err_handler)
