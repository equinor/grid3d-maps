import logging
from collections import defaultdict

import numpy as np
import numpy.ma as ma
import xtgeo
from xtgeo.common.exceptions import DateNotFoundError, KeywordFoundNoDateError

logger = logging.getLogger(__name__)

# Heavy need for reprogramming...:
# pylint: disable=logging-format-interpolation
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-nested-blocks


def files_to_import(config, appname):
    """Get a list of files to import, based on config"""

    folderroot = None
    if "folderroot" in config["input"] and config["input"]["folderroot"] is not None:
        folderroot = config["input"]["folderroot"]

    eclroot = None
    if "eclroot" in config["input"] and config["input"]["eclroot"] is not None:
        eclroot = config["input"]["eclroot"]

    gfile = ""
    initlist = {}
    restartlist = {}
    dates = []

    if eclroot:
        gfile = eclroot + ".EGRID"

    if "grid" in config["input"]:
        gfile = config["input"]["grid"]

    if appname == "grid3d_hc_thickness":
        if config["computesettings"]["mode"] == "rock":
            return gfile, initlist, restartlist, dates

        if "xhcpv" in config["input"]:
            initlist["xhcpv"] = config["input"]["xhcpv"]

        else:
            if eclroot is None:
                raise ValueError("'eclroot' information is not provided")

            initlist["PORO"] = eclroot + ".INIT"
            initlist["NTG"] = eclroot + ".INIT"
            initlist["PORV"] = eclroot + ".INIT"
            initlist["DX"] = eclroot + ".INIT"
            initlist["DY"] = eclroot + ".INIT"
            initlist["DZ"] = eclroot + ".INIT"
            if config["computesettings"]["critmode"]:
                crname = config["computesettings"]["critmode"].upper()
                initlist[crname] = eclroot + ".INIT"

            restartlist["SWAT"] = eclroot + ".UNRST"
            restartlist["SGAS"] = eclroot + ".UNRST"

            for date in config["input"]["dates"]:
                if len(date) == 8:
                    dates.append(date)
                elif len(date) > 12:
                    dates.append(date.split("-")[0])
                    dates.append(date.split("-")[1])

    if appname == "grid3d_average_map":
        # Put things in initlist or restart list. Only Eclipse
        # UNRST comes in the restartlist, all other in the initlist.
        # For instance, a ROFF parameter PRESSURE_20110101 will
        # technically be an initlist parameter here

        for item in config["input"]:
            if item == "folderroot":
                continue
            if item == "eclroot":
                continue
            if item == "grid":
                gfile = config["input"]["grid"]
                if "$folderroot" in gfile:
                    gfile = gfile.replace("$folderroot", folderroot)
                if "$eclroot" in gfile:
                    gfile = gfile.replace("$eclroot", eclroot)
            else:
                if "UNRST" in config["input"][item]:
                    if "--" in item:
                        param = item.split("--")[0]
                        date = item.split("--")[1]

                    rfile = config["input"][item]
                    if "$folderroot" in rfile:
                        rfile = rfile.replace("$folderroot", folderroot)
                    if "$eclroot" in rfile:
                        rfile = rfile.replace("$eclroot", eclroot)
                    restartlist[param] = rfile
                    # dates:
                    if len(date) > 10:
                        dates.append(date.split("-")[0])
                        dates.append(date.split("-")[1])
                    else:
                        dates.append(date)

                else:
                    ifile = config["input"][item]
                    if "$folderroot" in ifile:
                        ifile = ifile.replace("$folderroot", folderroot)
                    if "$eclroot" in ifile:
                        ifile = ifile.replace("$eclroot", eclroot)
                    initlist[item] = ifile

    dates = sorted(set(dates))  # to get a list with unique dates

    return gfile, initlist, restartlist, dates


def import_data(appname, gfile, initlist, restartlist, dates):
    """Get the grid and the props data.
    Well get the grid and the propsdata for data to be plotted,
    zonation (if required), filters (if required)

    Will return data on appropriate format...

    Args:
        config(dict): Th configuration dictionary
        appname(str): Name of application

    """
    logger.debug("Import data for %s", appname)
    # get the grid data + some geometrics
    grd = xtgeo.grid_from_file(gfile)

    # For rock thickness only model, the initlist and restartlist will be
    # empty dicts, and just return at this point.

    if not initlist and not restartlist:
        return grd, None, None, None

    # collect data per initfile etc: make a dict on the form:
    # {initfilename: [[prop1, lookfor1], [prop2, lookfor2], ...]} the
    # trick is defaultdict!
    #
    # The initfile itself may be a file or dictionary itself, e.g. either
    # SOME.INIT or {Name: somefile.roff}. In the latter, we should look for
    # Name in the file while doing the import.

    initdict = defaultdict(list)
    for ipar, ifile in initlist.items():
        if ipar == "fmu_global_config":
            continue
        if isinstance(ifile, dict):
            lookfor, usefile = list(ifile.keys()), list(ifile.values())
            initdict[usefile[0]].append([ipar, lookfor[0]])
        else:
            lookfor = ipar

            # if just a name: file.roff, than the name here and name in
            # the file may not match. So here it is assumed that "lookfor"
            # shall be None

            if ifile.endswith(".roff"):
                lookfor = None

            initdict[ifile].append([ipar, lookfor])

    restdict = defaultdict(list)
    for rpar, rfile in restartlist.items():
        logger.debug("Parameter RESTART: %s \t file is %s", rpar, rfile)
        restdict[rfile].append(rpar)

    initobjects = []
    for inifile, iniprops in initdict.items():
        if len(iniprops) > 1:
            lookfornames = []
            usenames = []
            for iniprop in iniprops:
                usename, lookforname = iniprop
                lookfornames.append(lookforname)
                usenames.append(usename)

            logger.info(f"Import <{lookfornames}> from <{inifile}> ...")
            tmp = xtgeo.gridproperties_from_file(
                inifile, names=lookfornames, fformat="init", grid=grd
            )
            for i, name in enumerate(lookfornames):
                prop = tmp.get_prop_by_name(name)
                prop.name = usenames[i]  # rename if different
                initobjects.append(prop)

        else:
            # single properties, typically ROFF stuff
            usename, lookforname = iniprops[0]

            # backward compatibility and flexibility; accept None, none, unknown, ...
            if lookforname and lookforname.lower() in {"none", "unknown"}:
                lookforname = None

            logger.info(f"Import <{lookforname}> from <{inifile}> ...")
            tmp = xtgeo.gridproperty_from_file(
                inifile, name=lookforname, fformat="guess", grid=grd
            )
            tmp.name = usename
            initobjects.append(tmp)

    logger.debug("Init type data is now imported for {}".format(appname))

    # restarts; will issue an warning if one or more dates are not found
    # assume that this is Eclipse stuff .UNRST
    restobjects = []

    for restfile, restprops in restdict.items():
        try:
            tmp = xtgeo.gridproperties_from_file(
                restfile, names=restprops, fformat="unrst", grid=grd, dates=dates
            )

        except DateNotFoundError as rwarn:
            logger.debug("Got warning... %s", rwarn)
            for prop in tmp.props:
                logger.debug("Append prop: {}".format(prop))
                restobjects.append(prop)
        except KeywordFoundNoDateError as rwarn:
            logger.debug("Keyword found but not for this date %s", rwarn)
            raise SystemExit("STOP") from rwarn
        except Exception as message:
            raise SystemExit(message) from message
        else:
            logger.debug("Works further...")
            for prop in tmp.props:
                logger.debug("Append prop: {}".format(prop))
                restobjects.append(prop)

    logger.debug("Restart type data is now imported for {}".format(appname))

    newdateslist = []
    for rest in restobjects:
        newdateslist.append(str(rest.date))  # assure date datatype is str

    newdateslist = list(set(newdateslist))
    logger.debug("Actual dates to use: {}".format(newdateslist))

    return grd, initobjects, restobjects, newdateslist


def import_filters(config, appname, grd):
    """Get the filterdata, and process them, return a filterarray

    If no filters are active, the filterarray will be 1 for all cells.

    Args:
        config(dict): Th configuration dictionary
        appname(str): Name of application
        grd (Grid): The XTGeo Grid obejct

    Returns:
        filterarray (ndarray): A 3D numpy array with 0 and 1 to be used as
            a multiplier.

    """

    eclroot = config["input"].get("eclroot")

    logger.debug("Import filter data for %s", appname)

    filterarray = np.ones(grd.dimensions, dtype="int")

    filterinfo = ""

    if "filters" not in config or not isinstance(config["filters"], list):
        config["_filterinfo"] = filterinfo  # perhaps not best practice...
        return filterarray

    for flist in config["filters"]:
        if "name" in flist:
            name = flist["name"]
            logger.debug("Filter name: %s", name)
            source = flist["source"]
            drange = flist.get("discrange", None)

            # drange may either be a list or a dict (or None):
            if isinstance(drange, dict):
                drangetxt = list(drange.values())
                drange = list(drange.keys())
            elif isinstance(drange, list):
                drangetxt = list(drange)

            irange = flist.get("intvrange", None)
            discrete = flist.get("discrete", False)
            filterinfo = filterinfo + "  " + name

            if "$eclroot" in source:
                source = source.replace("$eclroot", eclroot)
            gprop = xtgeo.gridproperty_from_file(source, grid=grd, name=name)
            pval = gprop.values
            logger.info("Filter, import <{}> from <{}> ...".format(name, source))

            if not discrete:
                filterarray[(pval < irange[0]) | (pval > irange[1])] = 0
                filterinfo = filterinfo + ":" + str(irange)
            else:
                # discrete variables can both be a range and discrete choice
                # i.e. intvrange vs discrange
                invarray = np.zeros(grd.dimensions, dtype="int")
                if drange and irange is None:
                    filterinfo = filterinfo + ":" + str(drangetxt)
                    for ival in drange:
                        if ival not in gprop.codes:
                            logger.warning(
                                "Filter codevalue {} is not present in "
                                "discrete property {}".format(ival, gprop.name)
                            )

                        invarray[pval == ival] = 1
                elif drange is None and irange:
                    filterinfo = filterinfo + ":" + str(irange)
                    invarray[(pval >= irange[0]) & (pval <= irange[1])] = 1
                else:
                    raise ValueError(
                        'Either "discrange" OR "intvrange" must ',
                        "be defined in input (not both)",
                    )

                filterarray[invarray == 0] = 0

        if "tvdrange" in flist:
            tvdrange = flist["tvdrange"]
            _xc, _yc, zc = grd.get_xyz(asmasked=False)
            filterinfo = filterinfo + "  " + "tvdrange: {}".format(tvdrange)

            filterarray[zc.values < tvdrange[0]] = 0
            filterarray[zc.values > tvdrange[1]] = 0
            logger.info(
                "Filter on tdvrange {} (rough; based on cell center)".format(tvdrange)
            )

    config["_filterinfo"] = filterinfo  # perhaps not best practice...

    return filterarray


def get_numpies_hc_thickness(config, grd, initobjects, restobjects, dates):
    """Process for HC thickness map; to get the needed numpies"""

    logger.debug("Getting numpies...")

    logger.debug("Getting actnum...")
    actnum = grd.get_actnum().values
    actnum = ma.filled(actnum)

    logger.debug("Getting xc, yc, zc...")
    xc, yc, zc = grd.get_xyz(asmasked=False)
    xc = ma.filled(xc.values)
    yc = ma.filled(yc.values)
    zc = ma.filled(zc.values)

    logger.debug("Getting dz...")
    dz = ma.filled(grd.get_dz(asmasked=False).values)
    logger.debug("Getting dz as ma.filled...")
    dz[actnum == 0] = 0.0

    logger.debug("Getting dx dy...")
    dx = ma.filled(grd.get_dx().values)
    dy = ma.filled(grd.get_dy().values)
    logger.debug("ma.filled for dx dy done")

    initd = {
        "iactnum": actnum,
        "xc": xc,
        "yc": yc,
        "zc": zc,
        "dx": dx,
        "dy": dy,
        "dz": dz,
    }

    logger.debug("Got {}".format(initd.keys()))

    if config["computesettings"]["critmode"]:
        crname = config["computesettings"]["critmode"].upper()
    else:
        crname = None

    xmode = config["computesettings"]["mode"]
    xmethod = config["computesettings"]["method"]
    xinput = config["input"]

    if "rock" in xmode:
        return initd, None

    if "xhcpv" in xinput:
        xhcpv = ma.filled(initobjects[0].values, fill_value=0.0)
        xhcpv[actnum == 0] = 0.0
        initd.update({"xhcpv": xhcpv})

    else:
        if xmethod == "use_poro" or xmethod == "use_porv":
            # initobjects is a list of GridProperty objects (single)
            for prop in initobjects:
                if prop.name == "PORO":
                    poro = ma.filled(prop.values, fill_value=0.0)
                if prop.name == "NTG":
                    ntg = ma.filled(prop.values, fill_value=0.0)
                if prop.name == "PORV":
                    porv = ma.filled(prop.values, fill_value=0.0)
                if prop.name == "DX":
                    dx = ma.filled(prop.values, fill_value=0.0)
                if prop.name == "DY":
                    dy = ma.filled(prop.values, fill_value=0.0)
                if prop.name == "DZ":
                    dz = ma.filled(prop.values, fill_value=0.0)
                if crname is not None and prop.name == crname:
                    soxcr = ma.filled(prop.values, fill_value=0.0)

            porv[actnum == 0] = 0.0
            poro[actnum == 0] = 0.0
            ntg[actnum == 0] = 0.0
            dz[actnum == 0] = 0.0

            initd.update(
                {"porv": porv, "poro": poro, "ntg": ntg, "dx": dx, "dy": dy, "dz": dz}
            )

            if crname is not None:
                initd["soxcr"] = soxcr
            else:
                initd["soxcr"] = None

    logger.debug("Got relevant INIT numpies, OK ...")

    # restart data, they have alos a date component:

    restartd = {}

    sgas = {}
    swat = {}
    soil = {}

    for date in dates:
        nsoil = 0
        for prop in restobjects:
            pname = "SWAT" + "_" + str(date)
            if prop.name == pname:
                swat[date] = ma.filled(prop.values, fill_value=1)
                nsoil += 1

            pname = "SGAS" + "_" + str(date)
            if prop.name == pname:
                sgas[date] = ma.filled(prop.values, fill_value=1)
                nsoil += 1

            if nsoil == 2:
                soil[date] = np.ones(sgas[date].shape, dtype=sgas[date].dtype)
                soil[date] = soil[date] - swat[date] - sgas[date]

                if crname is not None:
                    soil[date] = soil[date] - soxcr

        # numpy operations on the saturations
        for anp in [soil[date], sgas[date]]:
            anp[anp > 1.0] = 1.0
            anp[anp < 0.0] = 0.0
            anp[actnum == 0] = 0.0

        restartd["sgas_" + str(date)] = sgas[date]
        restartd["swat_" + str(date)] = swat[date]
        restartd["soil_" + str(date)] = soil[date]

    return initd, restartd


def get_numpies_avgprops(config, grd, initobjects, restobjects):
    """Process for average map; to get the needed numpies"""

    actnum = grd.get_actnum().get_npvalues3d(fill_value=0)
    # mask is False  to get values for all cells, also inactive
    xc, yc, zc = grd.get_xyz(asmasked=False)
    xc = xc.get_npvalues3d()
    yc = yc.get_npvalues3d()
    zc = zc.get_npvalues3d()
    dz = grd.get_dz(asmasked=False).get_npvalues3d()

    dz[actnum == 0] = 0.0

    # store these in a dict for special data (specd):
    specd = {"idz": dz, "ixc": xc, "iyc": yc, "izc": zc, "iactnum": actnum}

    if initobjects is not None and restobjects is not None:
        groupobjects = initobjects + restobjects
    elif initobjects is None and restobjects is not None:
        groupobjects = restobjects
    elif initobjects is not None and restobjects is None:
        groupobjects = initobjects
    else:
        raise ValueError("Both initiobjects and restobjects are None")

    propd = {}

    for pname in config["input"]:
        usepname = pname
        if pname in ("folderroot", "eclroot", "grid"):
            continue

        # initdata may also contain date if ROFF is input!
        if "--" in pname:
            name = pname.split("--")[0]
            date = pname.split("--")[1]

            # treating difference values
            if "-" in date:
                date1 = date.split("-")[0]
                date2 = date.split("-")[1]

                usepname1 = name + "_" + date1
                usepname2 = name + "_" + date2

                ok1 = False
                ok2 = False

                for prop in groupobjects:
                    if usepname1 == prop.name:
                        ptmp1 = prop.get_npvalues3d()
                        ok1 = True
                    if usepname2 == prop.name:
                        ptmp2 = prop.get_npvalues3d()
                        ok2 = True

                    if ok1 and ok2:
                        ptmp = ptmp1 - ptmp2
                        propd[pname] = ptmp

            # only one date
            else:
                for prop in groupobjects:
                    usepname = pname.replace("--", "_")
                    if usepname == prop.name:
                        ptmp = prop.get_npvalues3d()
                        propd[pname] = ptmp

        # no dates
        else:
            for prop in groupobjects:
                if usepname == prop.name:
                    ptmp = prop.get_npvalues3d()
                    propd[pname] = ptmp

    logger.debug("Return specd from {} is {}".format(__name__, specd.keys()))
    logger.debug("Return propd from {} is {}".format(__name__, propd.keys()))
    return specd, propd
