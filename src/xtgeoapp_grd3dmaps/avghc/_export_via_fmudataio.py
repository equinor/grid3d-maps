"""General functions that exports maps / plots using fmu-dataio."""
import os

import fmu.dataio as dataio
from xtgeo.common import XTGeoDialog

xtg = XTGeoDialog()

logger = xtg.functionlogger(__name__)


def export_avg_map_dataio(
    surf, name="unknown", unit="fraction", attribute="unknown-attribute"
):
    """Export avererage maps using dataio."""

    # this routine i dependent that the env varible FMU_GLOBAL_CONFIG is active
    if "FMU_GLOBAL_CONFIG" not in os.environ:
        raise RuntimeError("The env variable FMU_GLOBAL_CONFIG is not set.")

    edata = dataio.ExportData(
        name=name,
        unit=unit,
        content={"property": {"attribute": attribute, "is_discrete": False}},
        vertical_domain={"depth": "msl"},
        timedata=None,
        is_prediction=True,
        is_observation=False,
        tagname="average_" + attribute,
        verbosity="WARNING",
        workflow="xtgeoapp-grd3dmaps script average maps",
    )
    fname = edata.export(surf)
    xtg.say(f"Outout as fmu-dataio: {fname}")
    return fname
