# Copyright (c) 2016 ARM Limited, All Rights Reserved
# SPDX-License-Identifier: Apache-2.0

# Licensed under the Apache License, Version 2.0 (the "License"); 
# you may not use this file except in compliance with the License.

# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software 
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, 
# either express or implied.

from util import *

# Tests 'mbed import'
def test_import(mbed, testrepos):
    test1 = testrepos[0]
    popen(['python', mbed, 'import', test1, 'testimport'])

    assertls(mbed, 'testimport', [
        "[mbed]",
        "testimport",
        "`- test2",
        "   `- test3",
        "      `- test4",
    ])
