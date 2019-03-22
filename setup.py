# Copyright (c) 2016 ARM Limited, All Rights Reserved
# SPDX-License-Identifier: Apache-2.0

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.

import os
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="mbed-cli",
    version="1.10.0",
    description="Arm Mbed command line tool for repositories version control, publishing and updating code from remotely hosted repositories (GitHub, GitLab and mbed.com), and invoking Mbed OS own build system and export functions, among other operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://github.com/ARMmbed/mbed-cli',
    author='ARM mbed',
    author_email='support@mbed.org',
    packages=["mbed"],
    entry_points={
        'console_scripts': [
            'mbed=mbed.mbed:main',
            'mbed-cli=mbed.mbed:main',
        ]
    },
    python_requires='>=2.7.10,!=3.0.*,!=3.1.*,<4',
    classifiers=(
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ),
)
