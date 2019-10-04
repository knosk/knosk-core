#!/usr/bin/env python

# MIT License
#
# Copyright (c) 2019 knosk
# All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import sys
import setuptools

VERSION = '1.0.0a1'

try:
    from setuptools import setup

except ImportError:
    from distutils.core import setup

if sys.version_info <= (3, 5):
    error = "ERROR: knosk-core requires Python Version 3.6 or above...exiting."
    print(error, file=sys.stderr)
    sys.exit(1)


def readme():
    with open("README.md") as f:
        return f.read()


setuptools.setup(name="knosk-core",
                 version=VERSION,
                 description="Knosk dialog management framework",
                 long_description=readme(),
                 long_description_content_type='text/markdown',
                 author="Knosk team",
                 author_email="info@knosk.com",
                 url="https://github.com/knosk/knosk-core",
                 packages=["knosk", "knosk.choosers", "knosk.core", "knosk.fields", "knosk.matchers",
                           "knosk.suggesters"],
                 license="MIT",
                 platforms="Posix; MacOS X",
                 install_requires=['jinja2', 'python-dateutil'],
                 python_requires='>=3.6',
                 classifiers=["Development Status :: 1 - Planning",
                              "Intended Audience :: Developers",
                              "License :: OSI Approved :: MIT License",
                              "Operating System :: POSIX",
                              "Topic :: Communications :: Chat",
                              "Topic :: Text Processing :: Linguistic",
                              "Programming Language :: Python :: 3",
                              "Programming Language :: Python :: 3.6",
                              "Programming Language :: Python :: 3.7"],
                 )
