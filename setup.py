#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
import os
from glob import glob
from os.path import basename
from os.path import splitext

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()


def parse_requirements(filename):
    """Load requirements from a pip requirements file"""
    try:
        lineiter = (line.strip() for line in open(filename))
        return [line for line in lineiter if line and not line.startswith("#")]
    except IOError:
        return []


def src(x):
    root = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(root, x))


requirements = parse_requirements("requirements.txt")

setup_requirements = ["pytest-runner", "wheel", "setuptools_scm>=3.2.0"]

test_requirements = ["pytest"]

hc_function = "grid3d_hc_thickness=" "xtgeoapp_grd3dmaps.grid3d_hc_thickness:main"
avg_function = "grid3d_average_map=" "xtgeoapp_grd3dmaps.grid3d_average_map:main"


setup(
    name="xtgeoapp_grd3dmaps",
    use_scm_version={
        "root": src(""),
        "write_to": src("src/xtgeoapp_grd3dmaps/_theversion.py"),
    },
    description="Make HC thickness, avg maps, etc directly from 3D props",
    long_description=readme + "\n\n" + history,
    author="Equinor R&T",
    author_email="jriv@equinor.com",
    url="https://github.com/equinor/xtgeoapp_grd3dmaps",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    entry_points={"console_scripts": [hc_function, avg_function]},
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords="xtgeo",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    test_suite="tests",
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
