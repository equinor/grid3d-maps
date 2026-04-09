"""Conftest.py pytest setup."""

import shutil
from pathlib import Path

import pytest


def pytest_configure(config):
    import matplotlib as mpl

    mpl.use("Agg")


@pytest.fixture(scope="session")
def rootpath(request: pytest.FixtureRequest) -> Path:
    return request.config.rootpath


@pytest.fixture(scope="session")
def global_variables_path(rootpath: Path) -> Path:
    return rootpath / "tests/data/reek/global_variables.yml"


def pytest_runtest_setup(item):
    """Called for each test."""
    markers = [value.name for value in item.iter_markers()]

    # pytest.mark.requires_ert:
    if "requires_ert" in markers and not shutil.which("ert"):
        pytest.skip("Skip test if not ERT present (executable 'ert' is missing)")


@pytest.fixture()
def datatree(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    global_variables_path: Path,
) -> Path:
    """Create a tmp folder structure for testing."""

    shutil.copytree("tests/yaml", tmp_path / "tests" / "yaml")
    shutil.copytree("tests/data", tmp_path / "tests" / "data")

    fmuconfig_output_path = tmp_path / "fmuconfig/output"
    fmuconfig_output_path.mkdir(parents=True, exist_ok=True)

    shutil.copy2(global_variables_path, fmuconfig_output_path)

    print("Temporary folder: ", tmp_path)
    monkeypatch.chdir(tmp_path)
    return tmp_path
