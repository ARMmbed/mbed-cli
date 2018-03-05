
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

def assertprofile(mbed, profile):
    expected = '[mbed] {}'.format(profile)

    # write the profile
    popen(['python', mbed, 'config', 'profile', profile])
    # read the profile
    output = pquery(['python', mbed, 'config', 'profile']).strip()

    assert output == expected

# Tests `mbed config profile`
def testprofile(mbed):
    # need to mark dir as an mbed program
    popen(['python', mbed, 'config', 'root', '.'])

    assertprofile(mbed, 'mbed-os/tools/profiles/develop.json')
    assertprofile(mbed, 'mbed-os/tools/profiles/develop.json cxx11_profile.json')
