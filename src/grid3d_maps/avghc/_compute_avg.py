import getpass
import logging
from time import localtime, strftime

import numpy as np
import numpy.ma as ma
import xtgeo
from xtgeo.surface import RegularSurface
from xtgeoviz import quickplot

from ._export_via_fmudataio import export_avg_map_dataio

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_avg(config, specd, propd, dates, zonation, zoned, filterarray):
    """Compute a dictionary with average numpy per date

    It will return a dictionary per parameter and eventually dates
    """
    logger.debug("Dates is unused %s", dates)

    avgd = {}

    myavgzon = config["computesettings"]["tuning"]["zone_avg"]
    mycoarsen = config["computesettings"]["tuning"]["coarsen"]

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

    logger.info("Mapping ...")
    if len(propd) == 0 or len(zoned) == 0:
        raise RuntimeError("The dictionary <propd> or <zoned> is zero. Stop")

    for zname, zrange in zoned.items():
        logger.debug("ZNAME and ZRANGE are %s:  %s", zname, zrange)
        usezonation = zonation
        usezrange = zrange

        # in case of super zones:
        if isinstance(zrange, list):
            usezonation = zonation.copy()
            usezonation[:, :, :] = 0
            logger.debug(usezonation)
            for zr in zrange:
                usezonation[zonation == zr] = 888

            usezrange = 888

        if zname == "all":
            usezonation = zonation.copy()
            usezonation[:, :, :] = 999
            usezrange = 999

            if config["computesettings"]["all"] is not True:
                logger.debug("Skip <%s> (cf. computesettings: all)", zname)
                continue
        else:
            if config["computesettings"]["zone"] is not True:
                continue

        for propname, pvalues in propd.items():
            # filters get into effect by multyplying with DZ weight
            usedz = specd["idz"] * filterarray

            xmap.avg_from_3dprop(
                xprop=specd["ixc"],
                yprop=specd["iyc"],
                mprop=pvalues,
                dzprop=usedz,
                zoneprop=usezonation,
                zone_minmax=[usezrange, usezrange],
                zone_avg=myavgzon,
                coarsen=mycoarsen,
            )

            filename = None
            if config["output"]["mapfolder"] != "fmu-dataio":
                filename = _avg_filesettings(config, zname, propname, mode="map")

            usename = (zname, propname)

            if config["computesettings"]["mask_zeros"]:
                xmap.values = ma.masked_inside(xmap.values, -1e-30, 1e-30)

            avgd[usename] = xmap.copy()
            if filename is None:
                export_avg_map_dataio(avgd[usename], usename, config)
            else:
                logger.info("Map file to {}".format(filename))
                avgd[usename].to_file(filename)

    return avgd


def do_avg_plotting(config, avgd):
    """Do plotting via matplotlib to PNG (etc) (if requested)"""

    logger.info("Plotting ...")

    for names, xmap in avgd.items():
        # 'names' is a tuple as (zname, pname)
        zname = names[0]
        pname = names[1]

        plotfile = _avg_filesettings(config, zname, pname, mode="plot")

        pcfg = _avg_plotsettings(config, zname, pname)

        logger.info("Plot to {}".format(plotfile))

        usevrange = pcfg["valuerange"]

        faults = None
        if pcfg["faultpolygons"] is not None:
            try:
                fau = xtgeo.polygons_from_file(pcfg["faultpolygons"], fformat="guess")
                faults = {"faults": fau}
                logger.info("Use fault polygons")
            except OSError as err:
                logger.info(str(err))
                faults = None
                logger.info("No fault polygons")

        quickplot(
            xmap,
            filename=plotfile,
            title=pcfg["title"],
            subtitle=pcfg["subtitle"],
            infotext=pcfg["infotext"],
            xlabelrotation=pcfg["xlabelrotation"],
            minmax=usevrange,
            colormap=pcfg["colortable"],
            faults=faults,
        )


def _avg_filesettings(config, zname, pname, mode="root"):
    """Local function for map or plot file root name"""

    delim = "--"

    if config["output"]["lowercase"]:
        zname = zname.lower()
        pname = pname.lower()

    # pname may have a single '-' if it contains a date; replace with '_'
    # need to trick a bit by first replacing '--' (if delim = '--')
    # with '~~', then back again...
    pname = pname.replace(delim, "~~").replace("-", "_").replace("~~", delim)

    tag = ""
    if config["output"]["tag"]:
        tag = config["output"]["tag"] + "_"

    prefix = zname
    if prefix == "all" and config["output"]["prefix"]:
        prefix = config["output"]["prefix"]

    xfil = (prefix + delim + tag + "average" + "_" + pname).replace(" ", "")

    if mode == "root":
        return xfil

    if mode == "map":
        path = config["output"]["mapfolder"] + "/"
        xfil = xfil + ".gri"

    elif mode == "plot":
        path = config["output"]["plotfolder"] + "/"
        xfil = xfil + ".png"

    return path + xfil


def _avg_plotsettings(config, zname, pname):
    """Local function for plot additional info for AVG maps."""

    title = "Weighted average for " + pname + ", zone " + zname

    showtime = strftime("%Y-%m-%d %H:%M:%S", localtime())
    infotext = config["title"] + " - "
    infotext += getpass.getuser() + " " + showtime
    if config["output"]["tag"]:
        infotext += " (tag: " + config["output"]["tag"] + ")"

    xlabelrotation = None
    valuerange = (None, None)
    diffvaluerange = (None, None)
    colortable = "rainbow"
    xlabelrotation = 0
    fpolyfile = None

    if "xlabelrotation" in config["plotsettings"]:
        xlabelrotation = config["plotsettings"]["xlabelrotation"]

    # better perhaps:
    # xlabelrotation = config['plotsettings'].get('xlabelrotation', None)

    if "valuerange" in config["plotsettings"]:
        valuerange = tuple(config["plotsettings"]["valuerange"])

    if "diffvaluerange" in config["plotsettings"]:
        diffvaluerange = tuple(config["plotsettings"]["diffvaluerange"])

    if "faultpolygons" in config["plotsettings"]:
        fpolyfile = config["plotsettings"]["faultpolygons"]

    # there may be individual plotsettings per property per zone...
    if pname is not None and pname in config["plotsettings"]:
        pfg = config["plotsettings"][pname]

        if "valuerange" in pfg:
            valuerange = tuple(pfg["valuerange"])

        if "diffvaluerange" in pfg:
            diffvaluerange = tuple(pfg["diffvaluerange"])

        if "xlabelrotation" in pfg:
            xlabelrotation = pfg["xlabelrotation"]

        if "colortable" in pfg:
            colortable = pfg["colortable"]

        if "faultpolygons" in pfg:
            fpolyfile = pfg["faultpolygons"]

        if zname is not None and zname in config["plotsettings"][pname]:
            zfg = config["plotsettings"][pname][zname]

            if "valuerange" in zfg:
                valuerange = tuple(zfg["valuerange"])

            if "diffvaluerange" in zfg:
                diffvaluerange = tuple(zfg["diffvaluerange"])

            if "xlabelrotation" in zfg:
                xlabelrotation = zfg["xlabelrotation"]

            if "colortable" in zfg:
                colortable = zfg["colortable"]

            if "faultpolygons" in zfg:
                fpolyfile = zfg["faultpolygons"]

    subtitle = None
    if "_filterinfo" in config and config["_filterinfo"]:
        subtitle = config["_filterinfo"]

    # passing settings to a dictionary which is returned
    plotcfg = {}
    plotcfg["title"] = title
    plotcfg["subtitle"] = subtitle
    plotcfg["infotext"] = infotext
    plotcfg["valuerange"] = valuerange
    plotcfg["diffvaluerange"] = diffvaluerange
    plotcfg["xlabelrotation"] = xlabelrotation
    plotcfg["colortable"] = colortable
    plotcfg["faultpolygons"] = fpolyfile

    return plotcfg
