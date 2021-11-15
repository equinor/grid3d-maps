"""Conftest.py pytest setup."""
import os
import shutil

import pytest


@pytest.fixture(name="datatree", scope="session", autouse=True)
def fixture_datatree(tmp_path_factory):
    """Create a tmp folder structure for testing."""
    tmppath = tmp_path_factory.mktemp("grd3dmaps")

    shutil.copytree("tests/yaml", tmppath / "tests" / "yaml")
    shutil.copytree("tests/data", tmppath / "tests" / "data")

    print("Temporary folder: ", tmppath)
    os.chdir(tmppath)
    return tmppath


@pytest.fixture(name="erttree", scope="session", autouse=True)
def fixture_erttree(tmp_path_factory):
    """Create a tmp folder structure for testing ert connection."""
    tmppath = tmp_path_factory.mktemp("ertrun")

    shutil.copytree("tests/yaml", tmppath / "tests" / "yaml")
    shutil.copytree("tests/data", tmppath / "tests" / "data")

    print("Temporary folder: ", tmppath)
    os.chdir(tmppath)
    return tmppath
