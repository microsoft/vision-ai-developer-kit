# Copyright (c) 2018, The Linux Foundation. All rights reserved.
# Licensed under the BSD License 2.0 license. See LICENSE file in the project root for
# full license information.

from setuptools import setup, find_packages
import os
import shutil

_major = '0.0'
_minor = '0+dev'

shutil.copy('.license', 'LICENSE.txt')

if os.path.exists('major.version'):
    with open('major.version', 'rt') as bf:
        _major = str(bf.read()).strip()

if os.path.exists('minor.version'):
    with open('minor.version', 'rt') as bf:
        _minor = str(bf.read()).strip()

VERSION = '{}.{}'.format(_major, _minor)
NAME = "iotccsdk"

LONG_DESCRIPTION = 'Python IOTCC Software Development Kit'
DESCRIPTION = 'IOTCC SDK'

DEPENDENCIES = [ ]

setup_args = {
    'name': NAME,
    'version': VERSION,
    'description': DESCRIPTION,
    'long_description': LONG_DESCRIPTION,
    'include_package_data': True,
    'install_requires': [
        DEPENDENCIES
    ],
    'packages': find_packages(exclude=["*.tests"]),
    'zip_safe': False,
    'cmdclass': {
    },
    'keywords': [
        'iot',
        'ai',
        'camera',
    ],
    'license': 'BSD 2.0',
    'classifiers': [
        'Development Status :: 4 - Beta',
        'Framework :: IPython',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Multimedia :: Graphics',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
}

setup(**setup_args)
