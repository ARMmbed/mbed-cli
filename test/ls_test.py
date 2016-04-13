from util import *

# Tests 'neo ls' and provides sanity check of test framework
def test_ls(neo, testrepos):
    assertls(neo, 'test1', [
        "test1",
        "`- test2",
        "   `- test3",
        "      `- test4",
    ])
