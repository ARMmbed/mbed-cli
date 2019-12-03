# Copyright (c) 2016-2019 ARM Limited, All Rights Reserved
# SPDX-License-Identifier: Apache-2.0

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.

import os
from setuptools import setup
from setuptools import find_packages

NAME = 'mbed-cli'
__version__ = None

repository_dir = os.path.dirname(__file__)

# single source for project version information without side effects
with open(os.path.join(repository_dir, 'mbed', '_version.py')) as fh:
    exec(fh.read())

# .rst readme needed for pypi
with open(os.path.join(repository_dir, 'README.rst')) as fh:
    long_description = fh.read()

with open(os.path.join(repository_dir, 'requirements.txt')) as fh:
    requirements = fh.readlines()

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    author='Arm mbed',
    author_email='support@mbed.org',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: Software Development :: Embedded Systems',
        'Topic :: Software Development :: Object Brokering',
    ),
    description="Command line tool for interacting with Mbed OS projects",
    keywords="Mbed OS CLI",
    include_package_data=True,
    install_requires=requirements,
    license='Apache 2.0',
    long_description=long_description,
    name=NAME,
    packages=find_packages(),
    python_requires='>=2.7.10, !=3.4.1, !=3.4.2, <4',
    url="http://github.com/ARMmbed/mbed-cli",
    version=__version__,
    entry_points={
        'console_scripts': [
            'mbed=mbed.mbed:main',
            'mbed-cli=mbed.mbed:main',
        ]
    }
)
