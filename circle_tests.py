#!/usr/bin/env python

# Copyright (c) 2016 ARM Limited, All Rights Reserved
# SPDX-License-Identifier: Apache-2.0

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.

from __future__ import print_function

import os
import sys
import subprocess
import shutil
import yaml

def rmtree_readonly(directory):
    def remove_readonly(func, path, _):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    shutil.rmtree(directory, onerror=remove_readonly)

# Source tests from yaml config
tests = None
with open('.circleci/config.yml', 'r') as f:
    data = yaml.safe_load(f)

    # Read yaml tree
    if sys.version_info[0] == 3:
        tests = data['jobs']['py3']['steps']
    else:
        tests = data['jobs']['py2']['steps']

    # Filter command list to only contain commands
    tests = [item['run'] for item in list(filter(lambda x : type(x) is dict, tests))]

    # ... and replace new lines with ampersands
    tests = [item.replace('\n', ' && ') for item in tests]

# Exit if no tests are found
if tests == None:
    sys.exit(1)

# Ignore all tests found before `pip install -e`
startIndex = -1
for cmd in tests:
    if 'pip install -e' in cmd:
        startIndex = tests.index(cmd) + 1
        break

if startIndex == -1:
    sys.exit(1)

# Delete `.test` directory if it exists
cwd = os.path.abspath(os.path.dirname(__file__))

if os.path.exists(os.path.join(cwd, '.tests')):
    rmtree_readonly(os.path.join(cwd, '.tests'))
os.mkdir(os.path.join(cwd, '.tests'))

# Run tests
for cmd in tests[startIndex:]:
    os.chdir(cwd)
    print("\n----------\nEXEC: \"%s\" " % cmd)
    proc = subprocess.Popen(cmd, shell=True)
    proc.communicate()

    if proc.returncode != 0:
        print("\n------------\nERROR: \"%s\"" % cmd)
        sys.exit(1)
