from __future__ import annotations

from ert import (
    ForwardModelStepDocumentation,
    ForwardModelStepJSON,
    ForwardModelStepPlugin,
)

from grid3d_maps.avghc.grid3d_average_map import DESCRIPTION


class Grid3dAverageMap(ForwardModelStepPlugin):
    def __init__(self) -> None:
        super().__init__(
            name="GRID3D_AVERAGE_MAP",
            command=[
                "grid3d_average_map",
                "--config",
                "<CONFIG_AVGMAP>",
                "--eclroot",
                "<ECLROOT>",
            ],
            default_mapping={
                "<ECLROOT>": "",
            },
        )

    def validate_pre_realization_run(
        self, fm_step_json: ForwardModelStepJSON
    ) -> ForwardModelStepJSON:
        return fm_step_json

    def validate_pre_experiment(self, fm_step_json: ForwardModelStepJSON) -> None:
        pass

    @staticmethod
    def documentation() -> ForwardModelStepDocumentation | None:
        return ForwardModelStepDocumentation(
            category="modelling.reservoir",
            source_package="grid3d_maps",
            source_function_name="Grid3dAverageMap",
            description=DESCRIPTION,
            examples="""
Following is an example for extracting maps from the flow simulation grid
.. code-block:: console

  FORWARD_MODEL GRID3D_AVERAGE_MAP(<CONFIG_AVGMAP>=conf.yml, <ECLROOT>=<ECLBASE>)

where ECLBASE is already defined in your ERT config, pointing to the Eclipse/Flow
basename relative to RUNPATH.

.. note:: The <ECLROOT> argument is optional and can be omitted if sufficient
information is provided in the config, e.g. when extracting maps from a geological grid.
""",
        )
