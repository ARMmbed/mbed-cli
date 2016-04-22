from util import *

# Tests 'mbed ls' and provides sanity check of test framework
def test_ls(mbed, testrepos):
    assertls(mbed, 'test1', [
        "test1",
        "`- test2",
        "   `- test3",
        "      `- test4",
    ])
