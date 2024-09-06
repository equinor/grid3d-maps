from __future__ import annotations

from ert import (
    ForwardModelStepDocumentation,
    ForwardModelStepJSON,
    ForwardModelStepPlugin,
)

from grid3d_maps.aggregate.grid3d_migration_time import DESCRIPTION


class Grid3dMigrationTime(ForwardModelStepPlugin):
    def __init__(self) -> None:
        super().__init__(
            name="GRID3D_MIGRATION_TIME",
            command=[
                "grid3d_migration_time",
                "--config",
                "<CONFIG_MIGTIME>",
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
            source_function_name="Grid3dMigrationTime",
            description=DESCRIPTION,
            examples="""
.. code-block:: console

  FORWARD_MODEL GRID3D_MIGRATION_TIME(<CONFIG_MIGTIME>=conf.yml, <ECLROOT>=<ECLBASE>)

where ECLBASE is already defined in your ERT config, pointing to the Eclipse/Flow
basename relative to RUNPATH.
""",
        )
