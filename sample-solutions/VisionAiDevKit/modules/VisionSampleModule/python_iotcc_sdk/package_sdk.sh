# Copyright (c) 2018, The Linux Foundation. All rights reserved.
# Licensed under the BSD License 2.0 license. See LICENSE file in the project root for
# full license information.

rm -r *.egg-info/
python setup.py sdist --formats=gztar
cd dist/
tar -rvf *.tar.gz tests/
