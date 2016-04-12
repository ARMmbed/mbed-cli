from util import *

def test_remove(neo, teststructure):
    with cd('test1'):
        popen(['python', neo, 'remove', 'test2'])

    assertls(neo, 'test1', [
        "test1",
    ])

def test_import_after_remove(neo, teststructure):
    test_remove(neo, teststructure)
    mkcommit('test1')

    test1 = teststructure[0]
    popen(['python', neo, 'import', test1, 'testimport'])

    assertls(neo, 'testimport', [
        "testimport",
    ])
