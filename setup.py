#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
from glob import glob
from os.path import basename
from os.path import splitext

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

hc_function = ('grid3d_hc_thickness='
                'xtgeo_utils2.avghc.grid3d_hc_thickness:main')
avg_function = ('grid3d_average_map='
                'xtgeo_utils2.avghc.grid3d_average_map:main')


setup(
    name='xtgeo_utils2',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='Make HC thickness, avg maps, etc directly from 3D props',
    long_description=readme + '\n\n' + history,
    author="Jan C. Rivenaes",
    author_email='jriv@statoil.com',
    url='https://git.statoil.no/xtgeo/xtgeo-utils2',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    entry_points={
        'console_scripts':
        [hc_function, avg_function]
    },

    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords='xtgeo_utils2',
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
