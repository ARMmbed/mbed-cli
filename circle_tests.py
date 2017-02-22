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

tests = None
with open("circle.yml", "r") as f:
    types = yaml.load_all(f)
    for t in types:
        for k,v in t.items():
            if k == 'test':
                tests = v['override']

if tests:
    cwd = os.path.abspath(os.path.dirname(__file__))

    if os.path.exists(os.path.join(cwd, '.tests')):
        rmtree_readonly(os.path.join(cwd, '.tests'))
    os.mkdir(os.path.join(cwd, '.tests'))

    for cmd in tests:
        os.chdir(cwd)
        print("\n----------\nEXEC: \"%s\" " % cmd)
        proc = subprocess.Popen(cmd, shell=True)
        proc.communicate()

        if proc.returncode != 0:
            print("\n------------\nERROR: \"%s\"" % cmd)
            sys.exit(1)
