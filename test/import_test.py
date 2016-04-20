from util import *

# Tests 'neo import'
def test_import(neo, testrepos):
    test1 = testrepos[0]
    popen(['python', neo, 'import', test1, 'testimport'])

    assertls(neo, 'testimport', [
        "testimport",
        "`- test2",
        "   `- test3",
        "      `- test4",
    ])
