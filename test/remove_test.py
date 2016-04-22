from util import *

# Tests the result of 'mbed remove'
def test_remove(mbed, testrepos):
    with cd('test1'):
        popen(['python', mbed, 'remove', 'test2'])

    assertls(mbed, 'test1', [
        "test1",
    ])

# Tests if a repo can be imported correctly after 'mbed remove'
def test_import_after_remove(mbed, testrepos):
    test_remove(mbed, testrepos)
    mkcommit('test1')

    test1 = testrepos[0]
    popen(['python', mbed, 'import', test1, 'testimport'])

    assertls(mbed, 'testimport', [
        "testimport",
    ])
