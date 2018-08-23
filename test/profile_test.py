
# Copyright (c) 2016 ARM Limited, All Rights Reserved
# SPDX-License-Identifier: Apache-2.0

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.

from util import *
import re

@pytest.fixture
def empty(mbed):
    pquery(['python', mbed, 'config', 'root', '.'])

def config(mbed, *args):
    call = ('python', mbed) + args
    return pquery(call)

def assertunset(mbed, *args):
    assert config(mbed, *args).startswith(
        '[mbed] No default {} set'.format(args[-1]))

def assertconfig(mbed, var, value):
    if value is None:
        assertunset(mbed, 'config', var)
    else:
        config(mbed, 'config', var, value)
        assert config(mbed, 'config', var) == \
            '[mbed] {}\n'.format(value)

def assertprofile(mbed, value):
    if value is None:
        assertunset(mbed, 'profile')
    else:
        config(mbed, 'profile', value)
        assert config(mbed, 'profile') == \
            '[mbed] {}\n'.format(value)


def test_profile(mbed, empty):
    '''test `mbed profile`'''
    assertprofile(mbed, None)
    assertprofile(mbed, 'profile.json')
    assertprofile(mbed, 'mbed-os/tools/profiles/develop.json')
    assertprofile(mbed, 'mbed-os/tools/profiles/develop.json cxx11_profile.json')

def test_global_profile(mbed, empty):
    '''test `mbed profile --global`'''
    assert config(mbed, 'profile', '--global', '~/.mbed_global_profile') \
        == '[mbed] profile is a local-only option\n'

def test_config_profile(mbed, empty):
    '''test `mbed config profile`'''
    assertconfig(mbed, 'profile', None)
    assertconfig(mbed, 'profile', 'profile.json')
    assertconfig(mbed, 'profile', 'mbed-os/tools/profiles/develop.json')
    assertconfig(mbed, 'profile', 'mbed-os/tools/profiles/develop.json cxx11_profile.json')

def test_config_global_profile(mbed):
    '''attempting to configure a global profile should result in an error message'''
    assert config(mbed, 'config', '--global', 'profile', '~/.mbed_global_profile') \
        == '[mbed] profile is a local-only option\n'
