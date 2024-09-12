from __future__ import annotations

import ert

from grid3d_maps.forward_models import (
    Grid3dAverageMap,
    Grid3dHcThickness,
)

PLUGIN_NAME = "grid3d_maps"


@ert.plugin(name=PLUGIN_NAME)
def installable_workflow_jobs() -> dict[str, str]:
    return {}


@ert.plugin(name=PLUGIN_NAME)
def installable_forward_model_steps() -> list[ert.ForwardModelStepPlugin]:
    return [
        Grid3dHcThickness,
        Grid3dAverageMap,
    ]
