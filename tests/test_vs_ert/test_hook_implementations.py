"""Test suite for hook implementation."""
import os
import shutil
from pathlib import Path

import pytest

try:
    import ert  # noqa
except ImportError:
    try:
        import ert_shared  # noqa
    except ImportError:
        pytest.skip(
            "Not testing ERT hooks when ERT is not installed", allow_module_level=True
        )

import grid3d_maps.hook_implementations.jobs as jobs

try:
    from ert.shared.plugins.plugin_manager import ErtPluginManager
except ModuleNotFoundError:
    from ert_shared.plugins.plugin_manager import ErtPluginManager

EXPECTED_JOBS = {
    "GRID3D_AVERAGE_MAP": "grid3d_maps/config_jobs/GRID3D_AVERAGE_MAP",
    "GRID3D_HC_THICKNESS": "grid3d_maps/config_jobs/GRID3D_HC_THICKNESS",
    "GRID3D_AGGREGATE_MAP": "grid3d_maps/config_jobs/GRID3D_AGGREGATE_MAP",
    "GRID3D_MIGRATION_TIME": "grid3d_maps/config_jobs/GRID3D_MIGRATION_TIME",
}

SRC_PATH = Path(__file__).absolute().parent.parent.parent / "src"


@pytest.mark.requires_ert
def test_hook_implementations():
    """Test hook implementation."""
    pma = ErtPluginManager(plugins=[jobs])

    installable_jobs = pma.get_installable_jobs()
    for wf_name, wf_location in EXPECTED_JOBS.items():
        assert wf_name in installable_jobs
        assert installable_jobs[wf_name].endswith(wf_location)
        assert os.path.isfile(installable_jobs[wf_name])

    assert set(installable_jobs.keys()) == set(EXPECTED_JOBS.keys())

    expected_workflow_jobs = {}
    installable_workflow_jobs = pma.get_installable_workflow_jobs()
    for wf_name, wf_location in expected_workflow_jobs.items():
        assert wf_name in installable_workflow_jobs
        assert installable_workflow_jobs[wf_name].endswith(wf_location)

    assert set(installable_workflow_jobs.keys()) == set(expected_workflow_jobs.keys())


@pytest.mark.requires_ert
def test_job_config_syntax():
    """Check for syntax errors made in job configuration files"""
    for _, job_config in EXPECTED_JOBS.items():
        # Check (loosely) that double-dashes are enclosed in quotes:
        with open(os.path.join(SRC_PATH, job_config), encoding="utf8") as f_handle:
            for line in f_handle.readlines():
                if not line.strip().startswith("--") and "--" in line:
                    assert '"--' in line and " --" not in line


@pytest.mark.requires_ert
@pytest.mark.integration
def test_executables():
    """Test executables listed in job configurations exist in $PATH"""
    for _, job_config in EXPECTED_JOBS.items():
        with open(os.path.join(SRC_PATH, job_config), encoding="utf8") as f_handle:
            executable = f_handle.readlines()[0].split()[1]
            assert shutil.which(executable)


@pytest.mark.requires_ert
def test_hook_implementations_job_docs():
    """Testing hook job docs."""
    pma = ErtPluginManager(plugins=[jobs])

    installable_jobs = pma.get_installable_jobs()

    docs = pma.get_documentation_for_jobs()

    assert set(docs.keys()) == set(installable_jobs.keys())

    for job_name in installable_jobs.keys():
        assert docs[job_name]["description"] != ""
        assert docs[job_name]["category"] != "other"
