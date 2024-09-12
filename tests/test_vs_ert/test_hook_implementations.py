"""Test suite for hook implementation."""

import shutil

import pytest

try:
    from ert.plugins.plugin_manager import ErtPluginManager
except ImportError:
    pytest.skip(
        "Not testing ERT hooks when ERT is not installed", allow_module_level=True
    )

import grid3d_maps.hook_implementations.jobs as jobs
from grid3d_maps.forward_models import (
    Grid3dAverageMap,
    Grid3dHcThickness,
)

EXPECTED_JOBS = {
    "GRID3D_AVERAGE_MAP",
    "GRID3D_HC_THICKNESS",
}


@pytest.mark.requires_ert
def test_that_installable_fm_steps_work_as_plugins():
    """Test that the forward models are included as ERT plugin."""
    fms = ErtPluginManager(plugins=[jobs]).forward_model_steps

    assert Grid3dHcThickness in fms
    assert Grid3dAverageMap in fms

    assert len(fms) == len(EXPECTED_JOBS)


@pytest.mark.requires_ert
def test_hook_implementations():
    """Test hook implementation."""
    pma = ErtPluginManager(plugins=[jobs])

    installable_fm_step_jobs = [fms().name for fms in pma.forward_model_steps]
    assert set(installable_fm_step_jobs) == set(EXPECTED_JOBS)

    expected_workflow_jobs = {}
    installable_workflow_jobs = pma.get_installable_workflow_jobs()
    for wf_name, wf_location in expected_workflow_jobs.items():
        assert wf_name in installable_workflow_jobs
        assert installable_workflow_jobs[wf_name].endswith(wf_location)

    assert set(installable_workflow_jobs.keys()) == set(expected_workflow_jobs.keys())


@pytest.mark.requires_ert
@pytest.mark.integration
def test_executables():
    """Test executables listed in job configurations exist in $PATH"""
    pma = ErtPluginManager(plugins=[jobs])
    for fm_step in pma.forward_model_steps:
        # the executable should be equal to the job name, but in lowercase letter
        assert shutil.which(fm_step().executable)


@pytest.mark.requires_ert
def test_executable_names():
    """The executable names should be equal to the job name, but in lowercase letter"""
    pma = ErtPluginManager(plugins=[jobs])
    for fm_step in pma.forward_model_steps:
        assert fm_step().executable == fm_step().name.lower()


@pytest.mark.requires_ert
def test_hook_implementations_job_docs():
    """Testing hook job docs."""
    pma = ErtPluginManager(plugins=[jobs])

    for fm_step in pma.forward_model_steps:
        fm_step_doc = fm_step.documentation()
        assert fm_step_doc.description is not None
        assert fm_step_doc.category == "modelling.reservoir"
