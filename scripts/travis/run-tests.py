#!/usr/bin/env python
import os
from subprocess import check_call

_dname = os.path.dirname

REPO_ROOT = _dname(_dname(_dname(os.path.abspath(__file__))))
os.chdir(REPO_ROOT)


def run(command):
    return check_call(command, shell=True)


run('python ./tests/test.py')
