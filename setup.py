from setuptools import setup

def readme():
    with open ("README.md", "r") as fd:
        return fd.read()


setup(
    name="mbed",
    packages=["mbed"],
    version="1.0.0",
    url='http://github.com/ARMmbed/mbed-cli',
    author='ARM mbed',
    author_email='support@mbed.org',
    license='Apache2',
    entry_points={
        'console_scripts': [
            'mbed = mbed.mbed'
            ]
        },
    long_description=readme(),
    )