import os
import shutil
from pathlib import Path

import pytest


@pytest.fixture(name="sourcepath", scope="session", autouse=True)
def fixture_sourcepath():
    """Return original root path for tests."""
    testroot = Path(__file__).absolute().parent.parent
    print("Current path is ", testroot)
    return testroot


@pytest.fixture(name="datatree", scope="session", autouse=True)
def fixture_datatree(tmp_path_factory):
    """Create a tmp folder structure for testing."""
    tmppath = tmp_path_factory.mktemp("grd3dmaps")

    # tmppath.mkdir(parents=True, exist_ok=True)
    shutil.copytree("tests/yaml", tmppath / "tests" / "yaml")
    shutil.copytree("tests/data", tmppath / "tests" / "data")

    print("Temporary folder: ", tmppath)
    os.chdir(tmppath)
    return tmppath


@pytest.fixture(name="erttree", scope="session", autouse=True)
def fixture_erttree(tmp_path_factory):
    """Create a tmp folder structure for testing."""
    tmppath = tmp_path_factory.mktemp("ertrun")

    # tmppath.mkdir(parents=True, exist_ok=True)
    shutil.copytree("tests/yaml", tmppath / "tests" / "yaml")
    shutil.copytree("tests/data", tmppath / "tests" / "data")

    print("Temporary folder: ", tmppath)
    os.chdir(tmppath)
    return tmppath
