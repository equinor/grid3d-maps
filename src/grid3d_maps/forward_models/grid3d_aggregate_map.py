from __future__ import annotations

from ert import (
    ForwardModelStepDocumentation,
    ForwardModelStepJSON,
    ForwardModelStepPlugin,
)

from grid3d_maps.aggregate.grid3d_aggregate_map import DESCRIPTION


class Grid3dAggregateMap(ForwardModelStepPlugin):
    def __init__(self) -> None:
        super().__init__(
            name="GRID3D_AGGREGATE_MAP",
            command=[
                "grid3d_aggregate_map",
                "--config",
                "<CONFIG_AGGREGATE>",
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
            source_function_name="Grid3dAggregateMap",
            description=DESCRIPTION,
            examples="""
.. code-block:: console

  FORWARD_MODEL GRID3D_AGGREGATE_MAP(<CONFIG_AGGREGATE>=conf.yml, <ECLROOT>=<ECLBASE>)

where ECLBASE is already defined in your ERT config, pointing to the Eclipse/Flow
basename relative to RUNPATH.
""",
        )
