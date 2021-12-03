"""Conftest.py pytest setup."""
import os
import shutil

import pytest


def pytest_runtest_setup(item):
    """Called for each test."""
    markers = [value.name for value in item.iter_markers()]

    # pytest.mark.requires_ert:
    if "requires_ert" in markers:
        if not shutil.which("ert"):
            pytest.skip("Skip test if not ERT present (executable 'ert' is missing)")


@pytest.fixture(name="datatree", scope="module", autouse=True)
def fixture_datatree(tmp_path_factory):
    """Create a tmp folder structure for testing."""
    tmppath = tmp_path_factory.mktemp("grd3dmaps")

    shutil.copytree("tests/yaml", tmppath / "tests" / "yaml")
    shutil.copytree("tests/data", tmppath / "tests" / "data")

    print("Temporary folder: ", tmppath)
    os.chdir(tmppath)
    return tmppath
