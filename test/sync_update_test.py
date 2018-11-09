# Copyright (c) 2016 ARM Limited, All Rights Reserved
# SPDX-License-Identifier: Apache-2.0

# Licensed under the Apache License, Version 2.0 (the "License"); 
# you may not use this file except in compliance with the License.

# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software 
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, 
# either express or implied.

from util import *

# Tests if a 'mbed sync', commit, and 'mbed update' works on a simple file change
def test_sync_update(mbed, testrepos):
    test1 = testrepos[0]
    popen(['python', mbed, 'import', test1, 'testimport', '-vv'])

    with cd('test1/test2'):
        with open('hello', 'w') as f:
            f.write('hello\n')
        popen([scm(), 'add', 'hello'])
        popen(['python', mbed, 'sync', '-vv'])
        mkcommit()

    with cd('test1'):
        popen(['python', mbed, 'sync', '-vv'])
        mkcommit()

    with cd('testimport'):
        popen(['python', mbed, 'update', '-vv'])

    assert os.path.isfile('testimport/test2/hello')

# Tests if removing a library is carried over sync/update
def test_sync_update_remove(mbed, testrepos):
    test1 = testrepos[0]
    popen(['python', mbed, 'import', test1, 'testimport', '-vv'])

    with cd('test1/test2'):
        remove('test3')
        popen(['python', mbed, 'sync', '-vv'])
        mkcommit()

    with cd('test1'):
        popen(['python', mbed, 'sync', '-vv'])
        mkcommit()

    with cd('testimport'):
        popen(['python', mbed, 'update', '-vv'])

    assertls(mbed, 'testimport', [
        "[mbed]",
        "testimport",
        "`- test2",
    ])

# Tests if adding a library is carried over sync/update
def test_sync_update_add(mbed, testrepos):
    test1 = testrepos[0]
    popen(['python', mbed, 'import', test1, 'testimport', '-vv'])

    with cd('test1/test2'):
        copy('test3', 'testcopy')
        popen(['python', mbed, 'sync', '-vv'])
        mkcommit()

    with cd('test1'):
        popen(['python', mbed, 'sync', '-vv'])
        mkcommit()

    with cd('testimport'):
        popen(['python', mbed, 'update', '-vv'])

    assertls(mbed, 'testimport', [
        "[mbed]",
        "testimport",
        "`- test2",
        "   |- test3",
        "   |  `- test4",
        "   `- testcopy",
        "      `- test4",
    ])

# Tests if moving a library is carried over sync/update
def test_sync_update_move(mbed, testrepos):
    test1 = testrepos[0]
    popen(['python', mbed, 'import', test1, 'testimport', '-vv'])

    with cd('test1/test2'):
        move('test3', 'testmove')
        popen(['python', mbed, 'sync', '-vv'])
        mkcommit()

    with cd('test1'):
        popen(['python', mbed, 'sync', '-vv'])
        mkcommit()

    with cd('testimport'):
        popen(['python', mbed, 'update', '-vv'])

    assertls(mbed, 'testimport', [
        "[mbed]",
        "testimport",
        "`- test2",
        "   `- testmove",
        "      `- test4",
    ])

