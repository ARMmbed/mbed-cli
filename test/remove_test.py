from util import *

# Tests the result of 'neo remove'
def test_remove(neo, testrepos):
    with cd('test1'):
        popen(['python', neo, 'remove', 'test2'])

    assertls(neo, 'test1', [
        "test1",
    ])

# Tests if a repo can be imported correctly after 'neo remove'
def test_import_after_remove(neo, testrepos):
    test_remove(neo, testrepos)
    mkcommit('test1')

    test1 = testrepos[0]
    popen(['python', neo, 'import', test1, 'testimport'])

    assertls(neo, 'testimport', [
        "testimport",
    ])
