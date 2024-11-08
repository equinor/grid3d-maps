"""General functions that exports maps / plots using fmu-dataio."""

import json
import logging
import os
from pathlib import Path

import fmu.dataio as dataio
from fmu.config import utilities as ut

logger = logging.getLogger(__name__)


def _get_global_config(thisconfig):
    """Get the global config in different manners. Priority:

    (1) A setting inside the setup file: input: fmu_global_config: will win if present
    (2) FMU_GLOBAL_CONFIG_GRD3DMAPS exists as env variable. Will be second
    (3) FMU_GLOBAL_CONFIG as env variabel!
    """
    alternatives = [
        "[input][fmu_global_config] in setup file",
        "FMU_GLOBAL_CONFIG_GRD3DMAPS",
        "FMU_GLOBAL_CONFIG",
    ]

    alt = []
    if "input" in thisconfig:
        alt.append(thisconfig["input"].get("fmu_global_config"))
    else:
        alt.append(None)

    alt.append(os.environ.get("FMU_GLOBAL_CONFIG_GRD3DMAPS"))
    alt.append(os.environ.get("FMU_GLOBAL_CONFIG"))

    cfg = None

    for altno, description in enumerate(alternatives):
        alternative = alt[altno]
        logger.info("Global %s", alternative)
        if not alternative:
            continue

        if Path(alternative).is_file():
            cfg = ut.yaml_load(alternative)
            logger.info("Global no %s config from %s", alternative, description)
            break

        raise IOError(
            f"Config file does not exist: {alternative}, source is {description}"
        )

    if not cfg:
        raise RuntimeError("Not able lo load the global config!")

    return cfg


def export_avg_map_dataio(surf, nametuple, config):
    """Export avererage maps using dataio.

    Args:
        surf: XTGeo RegularSurface object
        nametuple: On form ('myzone1', 'PRESSURE--19991201') where the last
            is an identifier (nameid) for the metadata config
        config: The processed config setup for this script (i.e. not global_config)
    """

    zoneinfo, nameid = nametuple
    logger.debug("Processed config: \n%s", json.dumps(config, indent=4))

    fmu_global_config = _get_global_config(config)

    metadata = config["metadata"]
    if nameid not in metadata:
        logger.info("Dataio: Nameid missing %s", nametuple)
        raise ValueError(
            f"Seems that 'metadata' for {nameid} is missing! Cf. documentation"
        )

    mdata = metadata[nameid]
    name = mdata.get("name", "unknown_name")
    attribute = mdata.get("attribute", "unknown_attribute")
    unit = mdata.get("unit", "")
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
        config=fmu_global_config,
        name=zoneinfo,
        unit=unit,
        content={"property": {"attribute": attribute, "is_discrete": False}},
        vertical_domain={"depth": "msl"},
        timedata=tdata,
        is_prediction=True,
        is_observation=False,
        tagname=globaltag + "average_" + name,
        workflow="grid3d-maps script average maps",
    )
    fname = edata.export(surf)
    logger.info(f"Output as fmu-dataio: {fname}")
    return fname


def export_hc_map_dataio(surf, zname, date, hcmode, config):
    """Export hc thickness maps using dataio.

    Args:
        surf: XTGeo RegularSurface object
        nametuple: The zone name.
        date: The date tag
        config: The processed config setup
        hcmode: e.g. "oil", "gas"
    """

    logger.debug("Processed config: \n%s", json.dumps(config, indent=4))

    fmu_global_config = _get_global_config(config)

    mdata = config["metadata"]

    name = hcmode + "thickness"
    attribute = name
    unit = mdata.get("unit", "")

    tt1 = None
    tt2 = None
    if len(date) >= 8:
        tt1 = date[0:8]

    if len(date) > 8:
        tt2 = date[9:17]

    if tt1:
        tdata = [[tt1, "monitor"]]
    if tt2:
        tdata.append([tt2, "base"])

    globaltag = mdata.get("globaltag", "")
    globaltag = globaltag + "_" if globaltag else ""

    edata = dataio.ExportData(
        config=fmu_global_config,
        name=zname,
        content={"property": {"attribute": attribute, "is_discrete": False}},
        vertical_domain={"depth": "msl"},
        timedata=tdata,
        is_prediction=True,
        is_observation=False,
        unit=unit,
        tagname=globaltag + name,
        workflow="grid3d-maps script hc thickness maps",
    )
    fname = edata.export(surf)
    logger.info(f"Output as fmu-dataio: {fname}")
    return fname
