from util import *

def test_ls(neo, teststructure):
    assertls(neo, 'test1', [
        "test1",
        "`- test2",
        "   `- test3",
        "      `- test4",
    ])
