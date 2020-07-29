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
# THIS SOFTWARE IS PROVIDED 'AS IS' AND ANY EXPRESS OR IMPLIED
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
from os import path
from io import open

_packages = find_packages(exclude=['tests', 'test.*', '*.tests'])

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


NAME = 'iotccsdk'
VERSION = '0.1.4'
DESCRIPTION = 'SDK in Python for interacting with the Vision AI DevKit.'
PROJECT_URL = 'https://github.com/microsoft/vision-ai-developer-kit'
DEPENDENCIES = ['pip >= 9.0.0', 'requests',
                'setuptools-git', 'websocket-client']

setup_args = {
    'name': NAME,
    'version': VERSION,
    'description': DESCRIPTION,
    'long_description': long_description,
    'long_description_content_type': 'text/markdown',
    'url': PROJECT_URL,
    'include_package_data': True,
    'python_requires': '~=3.5',
    'install_requires': [
        DEPENDENCIES
    ],
    'packages': _packages,
    'package_data': {'sdk': ['logger.conf']},
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
        'Topic :: Multimedia :: Graphics :: Capture :: Digital Camera',
        'Topic :: Multimedia :: Video',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development',
        'Programming Language :: Python :: 3.5',
    ],
    'project_urls': {
        'Vision AI DevKit Page': 'https://azure.github.io/Vision-AI-DevKit-Pages/',
        'Get Started': 'https://azure.github.io/Vision-AI-DevKit-Pages/docs/Get_Started/'
    }
}

setup(**setup_args)
