from setuptools import setup

def readme():
    with open ("README.md", "r") as fd:
        return fd.read()


setup(
    name="neo",
    packages=["neo"],
    version="1.0.0",
    entry_points={
        'console_scripts': [
            'neo = neo.neo'
            ]
        },
    long_description=readme(),
    )
