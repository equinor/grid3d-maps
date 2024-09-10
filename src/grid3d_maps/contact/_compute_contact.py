import logging

import numpy as np
import xtgeo
from xtgeo.surface import RegularSurface

logger = logging.getLogger(__name__)


def gridmap_contact(config, specd, propd, dates):
    """Compute a contact as a gridded map surface"""

    if "templatefile" in config["mapsettings"]:
        xmap = xtgeo.surface_from_file(config["mapsettings"]["templatefile"])
        xmap.values = 0.0
    else:
        ncol = config["mapsettings"].get("ncol")
        nrow = config["mapsettings"].get("nrow")

        xmap = RegularSurface(
            xori=config["mapsettings"].get("xori"),
            yori=config["mapsettings"].get("yori"),
            ncol=ncol,
            nrow=nrow,
            xinc=config["mapsettings"].get("xinc"),
            yinc=config["mapsettings"].get("yinc"),
            values=np.zeros((ncol, nrow)),
        )
    logger.info(propd)
