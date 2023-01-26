"""General functions that exports maps / plots using fmu-dataio."""
import json
import os

import fmu.dataio as dataio
from fmu.config import utilities as util
from xtgeo.common import XTGeoDialog

xtg = XTGeoDialog()

logger = xtg.functionlogger(__name__)


def export_avg_map_dataio(surf, nametuple, config):
    """Export avererage maps using dataio.

    Args:
        surf: XTGeo RegularSurface object
        nametuple: On form ('myzone1', 'PRESSURE--19991201') where the last
            is an identifier (nameid) for the metadata config
        config: The processed config setup
    """

    zoneinfo, nameid = nametuple
    logger.debug("Processed config: \n%s", json.dumps(config, indent=4))

    # this routine is dependent that the env variable FMU_GLOBAL_CONFIG is active
    global_config = None
    if "global_config" in config["output"]:
        global_config = util.yaml_load(config["output"]["global_config"])

    if not global_config and "FMU_GLOBAL_CONFIG" not in os.environ:
        raise RuntimeError("The env variable FMU_GLOBAL_CONFIG is not set.")

    metadata = config["metadata"]
    if nameid not in metadata:
        raise ValueError(f"Seems that medata for {nameid} is missing!")

    mdata = metadata[nameid]
    name = mdata.get("name", "unknown_name")
    attribute = mdata.get("attribute", "unknown_attribute")
    unit = mdata.get("unit", None)
    tt1 = mdata.get("t1", None)
    tt2 = mdata.get("t2", None)
    if tt1 and tt1 not in nameid:
        tt1 = None
    if tt2 and tt2 not in nameid:
        tt2 = None

    globaltag = mdata.get("globaltag", "")
    globaltag = globaltag + "_" if globaltag else ""

    tdata = None
    if tt1:
        tdata = [[tt1, "monitor"]]
    if tt2:
        if tdata:
            tdata.append([tt2, "base"])
        else:
            tdata = [[tt2, "base"]]

    edata = dataio.ExportData(
        config=global_config,
        name=zoneinfo,
        unit=unit,
        content={"property": {"attribute": attribute, "is_discrete": False}},
        vertical_domain={"depth": "msl"},
        timedata=tdata,
        is_prediction=True,
        is_observation=False,
        tagname=globaltag + "average_" + name,
        verbosity="WARNING",
        workflow="xtgeoapp-grd3dmaps script average maps",
    )
    fname = edata.export(surf, unit=unit)
    xtg.say(f"Output as fmu-dataio: {fname}")
    return fname


def export_hc_map_dataio(surf, zname, date, hcmode, config):
    """Export hc thickness maps using dataio.

    Args:
        surf: XTGeo RegularSurface object
        nametuple: The zone name
        date: The date tag
        config: The processed config setup
        hcmode: e.g. "oil", "gas"
    """

    logger.debug("Processed config: \n%s", json.dumps(config, indent=4))

    # this routine is dependent that the env variable FMU_GLOBAL_CONFIG is active
    if "FMU_GLOBAL_CONFIG" not in os.environ:
        raise RuntimeError("The env variable FMU_GLOBAL_CONFIG is not set.")

    mdata = config["metadata"]

    name = hcmode + "thickness"
    attribute = name
    unit = mdata.get("unit", None)

    tt1 = None
    tt2 = None
    if len(date) >= 8:
        tt1 = date[0:8]

    if len(date) > 8:
        tt2 = date[9:16]

    if tt1:
        tdata = [[tt1, "monitor"]]
    if tt2:
        tdata.append([tt2, "base"])

    globaltag = mdata.get("globaltag", "")
    globaltag = globaltag + "_" if globaltag else ""

    edata = dataio.ExportData(
        name=zname,
        unit=unit,
        content={"property": {"attribute": attribute, "is_discrete": False}},
        vertical_domain={"depth": "msl"},
        timedata=tdata,
        is_prediction=True,
        is_observation=False,
        tagname=globaltag + name,
        verbosity="WARNING",
        workflow="xtgeoapp-grd3dmaps script hc thickness maps",
    )
    fname = edata.export(surf, unit=unit)
    xtg.say(f"Outout as fmu-dataio: {fname}")
    return fname
