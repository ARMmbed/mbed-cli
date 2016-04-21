from util import *

# Tests the result of 'neo add'
def test_add(neo, testrepos):
    test3 = testrepos[2]

    with cd('test1'):
        popen(['python', neo, 'add', test3])

    assertls(neo, 'test1', [
        "test1",
        "|- test2",
        "|  `- test3",
        "|     `- test4",
        "`- test3",
        "   `- test4",
    ])

# Tests if a repo can be imported correctly after 'neo add'
def test_import_after_add(neo, testrepos):
    test_add(neo, testrepos)
    mkcommit('test1')

    test1 = testrepos[0]
    popen(['python', neo, 'import', test1, 'testimport'])

    assertls(neo, 'testimport', [
        "testimport",
        "|- test2",
        "|  `- test3",
        "|     `- test4",
        "`- test3",
        "   `- test4",
    ])
