# Copyright (c) 2018-2019, The Linux Foundation. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#    * Neither the name of The Linux Foundation nor the names of its
#      contributors may be used to endorse or promote products derived
#      from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from setuptools import setup, find_packages
import os
import shutil

_major = '0.0'
_minor = '0+dev'
_packages = find_packages(exclude=["*.tests"])

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

DEPENDENCIES = ["pip >= 9.0.0", "requests", "setuptools-git"]

setup_args = {
    'name': NAME,
    'version': VERSION,
    'description': DESCRIPTION,
    'long_description': LONG_DESCRIPTION,
    'include_package_data': True,
    'python_requires': '~=3.5',
    'install_requires': [
        DEPENDENCIES
    ],
    'packages': _packages,
    'package_data': {'sdk': 'logger.conf'},
    'zip_safe': False,
    'cmdclass': {
    },
    'keywords': [
        'iot',
        'ai',
        'camera',
    ],
    'license': 'BSD-3-Clause',
    'classifiers': [
        'Development Status :: 4 - Beta',
        'Framework :: IPython',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Multimedia :: Graphics',
        'Programming Language :: Python :: 3.5',
    ],
}

setup(**setup_args)
