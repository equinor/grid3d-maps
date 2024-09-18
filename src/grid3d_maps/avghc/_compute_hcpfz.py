import logging

import numpy.ma as ma

logger = logging.getLogger(__name__)


def get_hcpfz(config, initd, restartd, dates, hcmode, filterarray):
    """Compute a dictionary with hcpfz numpy (per date)."""
    # There may be cases where dates are missing, e.g. if computing
    # directly from the stoiip parameter.

    # check numpy
    for key, val in initd.items():
        if isinstance(val, ma.MaskedArray):
            raise ValueError("Item {} is masked".format(key))

    if restartd is not None:
        for key, val in restartd.items():
            if isinstance(val, ma.MaskedArray):
                raise ValueError("Item {} is masked".format(key))

    hcpfzd = {}

    # use the given date from config if stoiip, giip, etc as info
    gdate = str(config["input"]["dates"][0])  # will give 'unknowndate' if unset

    if "rock" in hcmode:
        hcpfzd[gdate] = initd["dz"] * filterarray

    elif "xhcpv" in config["input"]:
        area = initd["dx"] * initd["dy"]
        area[area < 10.0] = 10.0
        hcpfzd[gdate] = initd["xhcpv"] * filterarray / area

    else:
        hcpfzd = _get_hcpfz_ecl(config, initd, restartd, dates, hcmode, filterarray)

    return hcpfzd


def _get_hcpfz_ecl(config, initd, restartd, dates, hcmode, filterarray):
    # local function, get data from Eclipse INIT and RESTART

    hcpfzd = {}

    shcintv = config["computesettings"]["shc_interval"]
    hcmethod = config["computesettings"]["method"]

    if not dates:
        logger.error("Dates are missing. Bug?")
        raise RuntimeError("Dates er missing. Bug?")

    for date in dates:
        if hcmode in ("oil", "gas"):
            usehc = restartd["s" + hcmode + "_" + str(date)]
        elif hcmode == "comb":
            usehc1 = restartd["s" + "oil" + "_" + str(date)]
            usehc2 = restartd["s" + "gas" + "_" + str(date)]
            usehc = usehc1 + usehc2
        else:
            raise ValueError(f"Invalid mode '{hcmode}'' in 'computesettings: method'")

        if hcmethod == "use_poro":
            usehc[usehc < shcintv[0]] = 0.0
            usehc[usehc > shcintv[1]] = 0.0
            hcpfzd[date] = (
                initd["poro"] * initd["ntg"] * usehc * initd["dz"] * filterarray
            )

        elif hcmethod == "use_porv":
            area = initd["dx"] * initd["dy"]
            area[area < 10.0] = 10.0
            usehc[usehc < shcintv[0]] = 0.0
            usehc[usehc > shcintv[1]] = 0.0
            hcpfzd[date] = initd["porv"] * usehc * filterarray / area

        elif hcmethod == "dz_only":
            usedz = initd["dz"].copy()
            usedz[usehc < shcintv[0]] = 0.0
            usedz[usehc > shcintv[1]] = 0.0
            hcpfzd[date] = usedz * filterarray

        elif hcmethod == "rock":
            usedz = initd["dz"].copy()
            hcpfzd[date] = usedz * filterarray

        else:
            raise ValueError(
                f"Unsupported method '{hcmethod}' in 'computesettings' method"
            )

    for key, val in hcpfzd.items():
        logger.info("hcpfzd.items: %s   %s", key, type(val))

    # An important issue here is that one may ask for difference dates,
    # not just dates. Hence need to iterate over the dates in the input
    # config and select the right one, and delete those that are not
    # relevant; e.g. one may ask for 20050816--19930101 but not for
    # 20050816; in that case the difference must be computed but
    # after that the 20050816 entry will be removed from the list

    cdates = config["input"]["dates"]

    for cdate in cdates:
        cdate = str(cdate)
        if "-" in cdate:
            dt1 = str(cdate.split("-")[0])
            dt2 = str(cdate.split("-")[1])
            if dt1 in hcpfzd and dt2 in hcpfzd:
                hcpfzd[cdate] = hcpfzd[dt1] - hcpfzd[dt2]
            else:
                logger.warning(
                    f"Cannot retrieve data for date {dt1} and/or {dt2}. "
                    "Some TSTEPs failed?"
                )

    alldates = hcpfzd.keys()

    purecdates = [str(cda) for cda in cdates if "--" not in str(cda)]
    pureadates = [str(adate) for adate in alldates if "--" not in str(adate)]

    for udate in pureadates:
        if udate not in purecdates:
            del hcpfzd[udate]

    return hcpfzd
