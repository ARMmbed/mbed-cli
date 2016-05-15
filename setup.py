# Copyright 2014-2015 ARM Limited
#
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.
import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="mbed-cli",
    packages=["mbed"],
    version="0.1.8",
    url='http://github.com/ARMmbed/mbed-cli',
    author='ARM mbed',
    author_email='support@mbed.org',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'mbed=mbed.mbed',
            'mbed-cli=mbed.mbed',
            'neo=mbed.mbed'
        ]
    },
    long_description=read('pypi_readme.rst'),
)