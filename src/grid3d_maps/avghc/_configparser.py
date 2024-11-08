import argparse
import copy
import datetime
import logging
import os.path
import sys

import yaml

from grid3d_maps.avghc._loader import ConstructorError, FMUYamlSafeLoader

logger = logging.getLogger(__name__)


def parse_args(args, appname, appdescr):
    """Parse command line arguments."""
    if args is None:
        args = sys.argv[1:]

    usetxt = appname + " --config some.yaml ... "

    parser = argparse.ArgumentParser(description=appdescr, usage=usetxt)

    parser.add_argument(
        "-c",
        "--config",
        dest="config",
        type=str,
        required=True,
        help="Config file on YAML format (required)",
    )

    parser.add_argument(
        "-f",
        "--folderroot",
        dest="folderroot",
        type=str,
        help="Folder root name for inputdata",
    )

    parser.add_argument(
        "-e",
        "--eclroot",
        dest="eclroot",
        type=str,
        help="Eclipse root name (includes case name)",
    )

    parser.add_argument(
        "--mapfolder", dest="mapfolder", type=str, help="Name of map output root"
    )

    parser.add_argument(
        "--plotfolder",
        dest="plotfolder",
        type=str,
        default=None,
        help="Name of plot output root",
    )

    parser.add_argument(
        "--zfile", dest="zfile", type=str, help="Explicit file (YAML) for zonation"
    )

    parser.add_argument(
        "--dump",
        dest="dumpfile",
        type=str,
        help="Dump the parsed config to a file (for qc)",
    )

    parser.add_argument(
        "--legacydateformat",
        dest="legacydateformat",
        action="store_true",
        help="Flag for legacy dateformat in output file "
        "names, such as 1991_01_01 instead of 19910101",
    )

    if appname == "grid3d_hc_thickness":
        parser.add_argument(
            "-d",
            "--dates",
            dest="dates",
            nargs="+",
            type=int,
            default=None,
            help="A list of dates on YYYYMMDD format",
        )

        parser.add_argument(
            "-m", "--mode", dest="mode", type=str, default=None, help="oil, gas or comb"
        )

    if len(args) < 2:
        parser.print_help()
        logger.info("QUIT")
        raise SystemExit

    return parser.parse_args(args)


# =============================================================================
# YAML config
# =============================================================================


def yconfig(inputfile, tmp=False, standard=False):
    """Read from YAML file, returns a dictionary."""

    if not os.path.isfile(inputfile):
        logger.critical("STOP! No such config file exists: %s", inputfile)
        raise SystemExit

    with open(inputfile, "r", encoding="utf8") as stream:
        if standard:
            config = yaml.safe_load(stream)
        else:
            try:
                config = yaml.load(stream, Loader=FMUYamlSafeLoader)
            except ConstructorError as errmsg:
                logger.error(errmsg)
                raise SystemExit from errmsg

    logger.info(f"Input config YAML file <{inputfile}> is read...")

    # if the file is a temporary file, delete:
    if tmp:
        os.remove(inputfile)

    return config


def yconfigdump(cfg, outfile):
    """Write a dictionary (config) to YAML file."""

    with open(outfile, "w", encoding="utf8") as stream:
        yaml.dump(cfg, stream, default_flow_style=False)


def prepare_metadata(config):
    """Initiate metadata block.

    The metadata are needed for fmu-dataio and will be initiated here. It will
    look like this:

    "metadata": {
        "SWAT--19991201-20010101": {      # identifier name in this package
            "name": "SWAT",               # generic property name
            "nameinfo"                    # e.g. "oilthickness"
            "source": "$eclroot.UNRST",   # info
            "t1": "19991201",             # timedata entry 1
            "t2": "20010101",             # timedata entry 2
            "content": "saturation",      # content info for sumo
            "unit": "fraction",           # unit info
            "globaltag": "avg2c"          # a global tag from output.tag
        },

    """
    newconfig = copy.deepcopy(config)
    # make an entry metadata for fmu-dataio
    newconfig["metadata"] = {}

    return newconfig


def dateformatting(config):
    """Special processing of dates.

    The issue is to treat dates both flexible and backward compatible.

    Example on the 'implemented' format:
        dates:
          - 19991201
          - 20010101-19991201

    The 'alternative' format; implicit the case if include from master YAML:
        dates:
          - 1999-02-01  # as datetime.date object!
        diffdates:
          - [2001-01-01, 1999-02-01]  # as list with 2 datetime.date objects!

    The 'alternative' form will be converted to the 'implemented' form here.

    """

    newconfig = copy.deepcopy(config)

    if "input" not in config:
        return newconfig

    newdates = []
    update = False

    if "dates" in config["input"]:
        update = True
        for entry in config["input"]["dates"]:
            if isinstance(entry, datetime.date):
                newdates.append(entry.strftime("%Y%m%d"))
            else:
                newdates.append(entry)

        del newconfig["input"]["dates"]

    if "diffdates" in config["input"]:
        update = True
        for entry in config["input"]["diffdates"]:
            if isinstance(entry, list) and len(entry) == 2:
                dd1, dd2 = entry
                if isinstance(dd1, datetime.date):
                    dd1 = dd1.strftime("%Y%m%d")
                if isinstance(dd2, datetime.date):
                    dd2 = dd2.strftime("%Y%m%d")
                newdates.append(dd1 + "-" + dd2)
        del newconfig["input"]["diffdates"]

    if update:
        newconfig["input"]["dates"] = []
        newconfig["input"]["dates"].extend(newdates)

    return newconfig


def propformatting(config):
    """Special processing of 'properties' list if present in input.

    This applies to the 'average' script.

    Example on the 'implemented' format::

       PORO: $eclroot.INIT
       PRESSURE--19991201: $eclroot.UNRST
       PRESSURE--20030101-19991201: $eclroot.UNRST

    The 'alternative' format; implicit the case if include from master YAML::

       properties:
         -
           name: PORO
           source: $eclroot.INIT
         -
           name: PRESSURE
           source: $eclroot.UNRST
           dates: !include_from global_config3a.yml::global.DATES
           diffdates: !include_from global_config3a.yml::global.DIFFDATES

    The 'alternative' form will be converted to the 'implemented' form here.

    """

    newconfig = copy.deepcopy(config)

    if "input" not in config or "properties" not in config["input"]:
        return newconfig

    for prop in config["input"]["properties"]:
        if "name" not in prop:
            raise KeyError('The "name" key is required in "properties"')
        if "source" not in prop:
            raise KeyError('The "source" key is required in "properties"')

        # metdata are fetched both from ordinary data (e.g. name, dates) and from the
        # new metadata block
        fetched_metadata = {"name": prop["name"], "source": prop["source"]}

        newdates = []
        if "dates" in prop:
            for entry in prop["dates"]:
                if isinstance(entry, datetime.date):
                    newdates.append(entry.strftime("%Y%m%d"))
                else:
                    newdates.append(entry)

        if "diffdates" in prop:
            for entry in prop["diffdates"]:
                if isinstance(entry, list) and len(entry) == 2:
                    dd1, dd2 = entry
                    if isinstance(dd1, datetime.date):
                        dd1 = dd1.strftime("%Y%m%d")
                    if isinstance(dd2, datetime.date):
                        dd2 = dd2.strftime("%Y%m%d")
                    newdates.append(dd1 + "-" + dd2)

        # get the addional metadata privded by user input under properties:
        if "metadata" in prop:
            fetched_metadata.update(prop["metadata"])

        namekey = prop["name"]
        namekeys = []
        datekeys = {}
        if newdates:
            for mydate in newdates:
                namekey = prop["name"] + "--" + mydate
                newconfig["input"][namekey] = prop["source"]
                namekeys.append(namekey)
                if len(mydate) == 8:
                    datekeys[namekey] = {"t1": mydate}
                else:
                    dd1 = mydate[:8]
                    dd2 = mydate[9:]
                    datekeys[namekey] = {"t1": dd1, "t2": dd2}

        else:
            newconfig["input"][namekey] = prop["source"]
            namekeys.append(namekey)

        if "tag" in config["output"]:
            fetched_metadata.update({"globaltag": config["output"]["tag"]})

        for nkey in namekeys:
            newconfig["metadata"][nkey] = copy.deepcopy(fetched_metadata)
            if nkey in datekeys:
                newconfig["metadata"][nkey].update(datekeys[nkey])

    del newconfig["input"]["properties"]

    return newconfig


def yconfig_override(config, args, appname):
    """Override the YAML config with command line options"""

    newconfig = copy.deepcopy(config)

    if args.eclroot:
        newconfig["input"]["eclroot"] = args.eclroot
        logger.info(
            "YAML config overruled... eclroot is now: <{}>".format(
                newconfig["input"]["eclroot"]
            )
        )

    if args.folderroot:
        newconfig["input"]["folderroot"] = args.folderroot
        logger.info(
            "YAML config overruled... folderroot is now: <{}>".format(
                newconfig["input"]["folderroot"]
            )
        )

    if args.zfile:
        newconfig["zonation"]["yamlfile"] = args.zfile
        logger.info(
            "YAML config overruled... zfile (yaml) is now: <{}>".format(
                newconfig["zonation"]["yamlfile"]
            )
        )

    if args.mapfolder:
        newconfig["output"]["mapfolder"] = args.mapfolder
        logger.info(
            "YAML config overruled... output:mapfolder is now: <{}>".format(
                newconfig["output"]["mapfolder"]
            )
        )

    if args.plotfolder:
        newconfig["output"]["plotfolder"] = args.plotfolder
        logger.info(
            "YAML config overruled... output:plotfolder is now: <{}>".format(
                newconfig["output"]["plotfolder"]
            )
        )

    if args.legacydateformat:
        newconfig["output"]["legacydateformat"] = args.legacydateformat

    if appname == "grid3d_hc_thickness" and args.dates:
        newconfig["input"]["dates"] = args.dates

    return newconfig


def yconfig_set_defaults(config, appname):
    """Override the YAML config with defaults where missing input."""

    newconfig = copy.deepcopy(config)

    # some defaults if data is missing...
    if "title" not in newconfig:
        newconfig["title"] = "SomeField"

    if "computesettings" not in newconfig:
        newconfig["computesettings"] = {}

    if "plotsettings" not in newconfig:
        newconfig["plotsettings"] = {}

    if "zonation" not in newconfig:
        newconfig["zonation"] = {}

    if "mapsettings" not in newconfig:
        newconfig["mapsettings"] = None

    if "output" not in newconfig:
        newconfig["output"] = {}

    if "mapfile" not in newconfig["output"]:
        newconfig["output"]["mapfile"] = "hc_thickness"

    if "plotfile" not in newconfig["output"]:
        newconfig["output"]["plotfile"] = None

    if "legacydateformat" not in newconfig["output"]:
        newconfig["output"]["legacydateformat"] = False

    if "mapfolder" not in newconfig["output"]:
        newconfig["output"]["mapfolder"] = "fmu-dataio"  # Was /tmp

    if "plotfolder" not in newconfig["output"]:
        newconfig["output"]["plotfolder"] = None

    if "tag" not in newconfig["output"]:
        newconfig["output"]["tag"] = None

    if "prefix" not in newconfig["output"]:
        newconfig["output"]["prefix"] = None

    if "lowercase" not in newconfig["output"]:
        newconfig["output"]["lowercase"] = True

    if "tuning" not in newconfig["computesettings"]:
        newconfig["computesettings"]["tuning"] = {}

    if "mask_zeros" not in newconfig["computesettings"]:
        newconfig["computesettings"]["mask_zeros"] = False

    if "zname" not in newconfig["zonation"]:
        newconfig["zonation"]["zname"] = "all"

    if "yamlfile" not in newconfig["zonation"]:
        newconfig["zonation"]["yamlfile"] = None

    if "zonefile" not in newconfig["zonation"]:
        newconfig["zonation"]["zonefile"] = None

    if "zone_avg" not in newconfig["computesettings"]["tuning"]:
        newconfig["computesettings"]["tuning"]["zone_avg"] = False

    if "coarsen" not in newconfig["computesettings"]["tuning"]:
        newconfig["computesettings"]["tuning"]["coarsen"] = 1

    if appname == "grid3d_hc_thickness":
        if "dates" not in newconfig["input"]:
            if newconfig["computesettings"]["mode"] in "rock":
                logger.info('No date give, probably OK since "rock" mode)')
            else:
                logger.warning('Warning: No date given, set date to "unknowndate")')

            newconfig["input"]["dates"] = ["unknowndate"]

        if "mode" not in newconfig["computesettings"]:
            newconfig["computesettings"]["mode"] = "oil"

        if "method" not in newconfig["computesettings"]:
            newconfig["computesettings"]["method"] = "use_poro"

        if "unit" not in newconfig["computesettings"]:
            newconfig["computesettings"]["unit"] = "m"

        if "mask_outside" not in newconfig["computesettings"]:
            newconfig["computesettings"]["mask_outside"] = False

        if "shc_interval" not in newconfig["computesettings"]:
            newconfig["computesettings"]["shc_interval"] = [0.0001, 1.0]

        if "critmode" not in newconfig["computesettings"]:
            newconfig["computesettings"]["critmode"] = None

        if newconfig["computesettings"]["critmode"] is False:
            newconfig["computesettings"]["critmode"] = None

        if "zone" not in newconfig["computesettings"]:
            newconfig["computesettings"]["zone"] = False

        if "all" not in newconfig["computesettings"]:
            newconfig["computesettings"]["all"] = True

        # be generic if direct calculation is applied
        xlist = ("stooip", "goip", "hcpv", "stoiip", "giip")
        for xword in xlist:
            if xword in newconfig["input"]:
                newconfig["input"]["xhcpv"] = newconfig["input"][xword]
                break

    # treat dates as strings, not ints
    if "dates" in config["input"]:
        dlist = []
        for date in config["input"]["dates"]:
            dlist.append(str(date))

        newconfig["input"]["dates"] = dlist

    return newconfig


def yconfig_addons(config, appname):
    """Addons e.g. YAML import spesified in the top config."""

    newconfig = copy.deepcopy(config)

    if config["zonation"]["yamlfile"] is not None:
        # re-use yconfig:
        zconfig = yconfig(config["zonation"]["yamlfile"])
        if "zranges" in zconfig:
            newconfig["zonation"]["zranges"] = zconfig["zranges"]
        if "superranges" in zconfig:
            newconfig["zonation"]["superranges"] = zconfig["superranges"]

    logger.info(f"Add configuration to {appname}")

    return newconfig


def yconfig_metadata_hc(config):
    """Collect general metadata for HC thickness script.

    Metadata for HC maps is easier to derive as the output is known in advance; hence
    there seems to be almost no need for user spesified metadata, perhaps only 'unit'
    which can be given in computesettings block in input.

    Note that date and zone info will be added in map plotting loop, later.
    """

    newconfig = copy.deepcopy(config)
    attribute = config["computesettings"]["mode"] + "thickness"  # e.g. oilthickness

    newconfig["metadata"]["nameinfo"] = attribute
    newconfig["metadata"]["unit"] = config["computesettings"]["unit"]
    newconfig["metadata"]["globaltag"] = config["output"].get("tag", "")

    return newconfig
    return newconfig
