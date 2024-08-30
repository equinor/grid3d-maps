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
.. code-block:: console

  FORWARD_MODEL GRID3D_AVERAGE_MAP(<CONFIG_AVGMAP>=conf.yml, <ECLROOT>=<ECLBASE>)
""",
        )
