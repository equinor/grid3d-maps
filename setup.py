#!/usr/bin/env python

"""The setup script."""
import os
from glob import glob
from os.path import basename, splitext
from pathlib import Path

from setuptools import find_packages, setup

from scripts import setup_functions as setupx

CMDCLASS = {"clean": setupx.CleanUp}

APPS = ("grid3d_hc_thickness", "grid3d_average_map")

with open("README.rst", encoding="utf8") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst", encoding="utf8") as history_file:
    history = history_file.read()


REQUIREMENTS = setupx.parse_requirements("requirements/requirements.txt")
REQUIREMENTS_SETUP = setupx.parse_requirements("requirements/requirements_setup.txt")
REQUIREMENTS_TESTS = setupx.parse_requirements("requirements/requirements_tests.txt")
REQUIREMENTS_DOCS = setupx.parse_requirements("requirements/requirements_docs.txt")
REQUIREMENTS_EXTRAS = {"tests": REQUIREMENTS_TESTS, "docs": REQUIREMENTS_DOCS}

HC_FUNCTION = "grid3d_hc_thickness=xtgeoapp_grd3dmaps.avghc.grid3d_hc_thickness:main"
AVG_FUNCTION = "grid3d_average_map=xtgeoapp_grd3dmaps.avghc.grid3d_average_map:main"
AGG_FUNCTION = "grid3d_aggregate_map=xtgeoapp_grd3dmaps.avghc.grid3d_aggregate_map:main"
MIG_FUNCTION = "grid3d_migration_time=xtgeoapp_grd3dmaps.avghc.grid3d_migration_time:main"


def src(anypath):
    """Find src folders."""
    return Path(__file__).parent / anypath


setup(
    name="xtgeoapp_grd3dmaps",
    use_scm_version={
        "root": src(""),
        "write_to": src("src/xtgeoapp_grd3dmaps/_theversion.py"),
    },
    description="Make HC thickness, avg maps, etc directly from 3D props",
    long_description=readme + "\n\n" + history,
    author="Equinor R&T",
    license="GPLv3",
    url="https://github.com/equinor/xtgeoapp_grd3dmaps",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    entry_points={
        "console_scripts": [HC_FUNCTION, AVG_FUNCTION, AGG_FUNCTION, MIG_FUNCTION],
        "ert": [
            "xtgeoapp_grd3dmaps_jobs = xtgeoapp_grd3dmaps.hook_implementations.jobs"
        ],
    },
    cmdclass=CMDCLASS,
    command_options=setupx.CMDSPHINX,
    include_package_data=True,
    zip_safe=False,
    keywords="xtgeo",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    test_suite="tests",
    install_requires=REQUIREMENTS,
    tests_require=REQUIREMENTS_TESTS,
    setup_requires=REQUIREMENTS_SETUP,
    extras_requires=REQUIREMENTS_EXTRAS,
)
