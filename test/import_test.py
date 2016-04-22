from util import *

# Tests 'mbed import'
def test_import(mbed, testrepos):
    test1 = testrepos[0]
    popen(['python', mbed, 'import', test1, 'testimport'])

    assertls(mbed, 'testimport', [
        "testimport",
        "`- test2",
        "   `- test3",
        "      `- test4",
    ])
