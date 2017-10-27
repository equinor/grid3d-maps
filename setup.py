#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
import versioneer

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    # TODO: put package requirements here
]

setup_requirements = [
    'pytest-runner',
    # TODO(jriv): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest',
    # TODO: put package test requirements here
]

setup(
    name='xtgeo_grid3d_map_apps',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='Make HC thickness, avg maps, etc directly from 3D props',
    long_description=readme + '\n\n' + history,
    author="Jan C. Rivenaes",
    author_email='jriv@statoil.com',
    url='https://git.statoil.no/xtgeo/xtgeo-grid3d-map-apps',
    packages=find_packages(include=['xtgeo_grid3d_map_apps']),
    # entry_points={
    #     'console_scripts':
    #     ['grid3d_hc_thickness=xtgeo_grid3d_map_apps.grid3d_hc_thickness:main',
    #      'grid3d_average_map=xtgeo_grid3d_map_apps.grid3d_hc_thickness:main']
    # },

    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords='xtgeo_grid3d_map_apps',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
