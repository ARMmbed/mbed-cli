# Copyright (c) 2016 ARM Limited, All Rights Reserved
# SPDX-License-Identifier: Apache-2.0

# Licensed under the Apache License, Version 2.0 (the "License"); 
# you may not use this file except in compliance with the License.

# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software 
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, 
# either express or implied.

from __future__ import print_function

import contextlib
import subprocess
import pytest
import os
import re
import shutil
import stat

MBED_PATH = os.path.abspath(os.path.join('mbed', 'mbed.py'))

# Process execution
class ProcessException(Exception):
    pass

def popen(command, stdin=None, **kwargs):
    print(' '.join(command))
    proc = subprocess.Popen(command, **kwargs)

    if proc.wait() != 0:
        raise ProcessException(proc.returncode)

def pquery(command, stdin=None, **kwargs):
    print(' '.join(command))
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
    stdout, _ = proc.communicate(stdin)

    if proc.returncode != 0:
        raise ProcessException(proc.returncode)

    return stdout.decode("utf-8")

# Directory navigation
@contextlib.contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(newdir)
    try:
        yield
    finally:
        os.chdir(prevdir)

# Handling test environment
@pytest.fixture
def mbed(tmpdir):
    tmpdir.chdir()

    return MBED_PATH
    
# Higher level functions
def remove(path):
    def remove_readonly(func, path, _):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    shutil.rmtree(path, onerror=remove_readonly)
    
def move(src, dst):
    shutil.move(src, dst)
    
def copy(src, dst):
    shutil.copytree(src, dst)

# Test specific utils
def mkgit(name):
    os.mkdir(name)
    with cd(name):
        popen(['git', 'init'])
        with open('test', 'w') as f:
            f.write('hello')
        popen(['git', 'add', 'test'])
        popen(['git', 'commit', '-m', '"commit 1"'])

    bare = os.path.abspath(name + '.git')
    popen(['git', 'clone', '--bare', name, bare])
    remove(name)
    return os.path.abspath(bare).replace('\\', '/')

def mkhg(name):
    os.mkdir(name+'.hg')
    with cd(name+'.hg'):
        popen(['hg', 'init'])
        with open('test', 'w') as f:
            f.write('hello')
        popen(['hg', 'add', 'test'])
        popen(['hg', 'commit', '-m', '"commit 1"'])

    return os.path.abspath(name+'.hg').replace('\\', '/')

def assertls(mbed, dir, tree):
    tree = ''.join(re.escape(l)+r'.*\n' for l in tree)

    with cd(dir):
        result = pquery(['python', mbed, 'ls'])

    print(result)
    assert re.match(tree, result, re.MULTILINE)

def scm(dir=None):
    if not dir:
        dir = os.getcwd()

    if os.path.isdir(os.path.join(dir, '.git')):
        return 'git'
    elif os.path.isdir(os.path.join(dir, '.hg')):
        return 'hg'

def mkcommit(dir=None, files=[]):
    with cd(dir or os.getcwd()):
        if scm() == 'git':
            if files:
                popen(['git', 'add'] + files)
            popen(['git', 'commit', '-a', '-m', 'test commit'])
            popen(['git', 'push', 'origin', 'master'])
        elif scm() == 'hg':
            if files:
                popen(['hg', 'add'] + files)
            popen(['hg', 'commit', '-m', 'test commit'])
            popen(['hg', 'push'])

# Different repository structures
@pytest.fixture(params=['git1', 'hg1', 'alt1', 'alt2'])
def testrepos(mbed, request):
    if request.param in ['git1', 'alt1']:
        test1 = mkgit('test1')
        popen(['git', 'clone', test1, 'test1'])
    else:
        test1 = mkhg('test1')
        popen(['hg', 'clone', test1, 'test1'])

    if request.param in ['git1', 'alt2']:
        test2 = mkgit('test2')
        popen(['git', 'clone', test2, 'test1/test2'])
    else:
        test2 = mkhg('test2')
        popen(['hg', 'clone', test2, 'test1/test2'])

    if request.param in ['git1', 'alt1']:
        test3 = mkgit('test3')
        popen(['git', 'clone', test3, 'test1/test2/test3'])
    else:
        test3 = mkhg('test3')
        popen(['hg', 'clone', test3, 'test1/test2/test3'])

    if request.param in ['git1', 'alt2']:
        test4 = mkgit('test4')
        popen(['git', 'clone', test4, 'test1/test2/test3/test4'])
    else:
        test4 = mkhg('test4')
        popen(['hg', 'clone', test4, 'test1/test2/test3/test4'])

    with cd('test1/test2/test3'):
        with open('test4.lib', 'w') as f:
            hash = 'none'
            with cd('test4'):
                if scm() == 'git':
                    hash = pquery(['git', 'rev-parse', 'HEAD'])
                elif scm() == 'hg':
                    hash = pquery(['hg', 'id', '-i'])
            f.write(test4 + '/#' + hash + '\n')

        if scm() == 'git':
            popen(['git', 'add', 'test4.lib'])
            popen(['git', 'commit', '-m', 'test commit'])
            popen(['git', 'push', 'origin', 'master'])
        elif scm() == 'hg':
            popen(['hg', 'add', 'test4.lib'])
            popen(['hg', 'commit', '-m', 'test commit'])
            popen(['hg', 'push'])
    
    with cd('test1/test2'):
        with open('test3.lib', 'w') as f:
            with cd('test3'):
                if scm() == 'git':
                    hash = pquery(['git', 'rev-parse', 'HEAD'])
                elif scm() == 'hg':
                    hash = pquery(['hg', 'id', '-i'])
            f.write(test3 + '/#' + hash + '\n')

        if scm() == 'git':
            popen(['git', 'add', 'test3.lib'])
            popen(['git', 'commit', '-m', 'test commit'])
            popen(['git', 'push', 'origin', 'master'])
        elif scm() == 'hg':
            popen(['hg', 'add', 'test3.lib'])
            popen(['hg', 'commit', '-m', 'test commit'])
            popen(['hg', 'push'])

    with cd('test1'):
        with open('test2.lib', 'w') as f:
            with cd('test2'):
                if scm() == 'git':
                    hash = pquery(['git', 'rev-parse', 'HEAD'])
                elif scm() == 'hg':
                    hash = pquery(['hg', 'id', '-i'])
            f.write(test2 + '/#' + hash + '\n')

        if scm() == 'git':
            popen(['git', 'add', 'test2.lib'])
            popen(['git', 'commit', '-m', 'test commit'])
            popen(['git', 'push', 'origin', 'master'])
        elif scm() == 'hg':
            popen(['hg', 'add', 'test2.lib'])
            popen(['hg', 'commit', '-m', 'test commit'])
            popen(['hg', 'push'])

    return test1, test2, test3, test4

