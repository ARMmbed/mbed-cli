from util import *

def test_import(neo, teststructure):
    test1 = teststructure[0]
    popen(['python', neo, 'import', test1, 'testimport'])

    assertls(neo, 'testimport', [
        "testimport",
        "`- test2",
        "   `- test3",
        "      `- test4",
    ])
