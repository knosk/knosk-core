#!/usr/bin/env python
import os
from subprocess import check_call
import shutil

_dname = os.path.dirname

REPO_ROOT = _dname(_dname(_dname(os.path.abspath(__file__))))
os.chdir(REPO_ROOT)


def run(command):
    return check_call(command, shell=True)


run('pip install -r requirements.txt')
run('pip install setuptools wheel')

if os.path.isdir('dist') and os.listdir('dist'):
    shutil.rmtree('dist')
if os.path.isdir('build') and os.listdir('build'):
    shutil.rmtree('build')
if os.path.isdir('knosk_core.egg-info') and os.listdir('knosk_core.egg-info'):
    shutil.rmtree('knosk_core.egg-info')

run('python setup.py sdist bdist_wheel')
