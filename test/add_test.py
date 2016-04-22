from util import *

# Tests the result of 'mbed add'
def test_add(mbed, testrepos):
    test3 = testrepos[2]

    with cd('test1'):
        popen(['python', mbed, 'add', test3])

    assertls(mbed, 'test1', [
        "test1",
        "|- test2",
        "|  `- test3",
        "|     `- test4",
        "`- test3",
        "   `- test4",
    ])

# Tests if a repo can be imported correctly after 'mbed add'
def test_import_after_add(mbed, testrepos):
    test_add(mbed, testrepos)
    mkcommit('test1')

    test1 = testrepos[0]
    popen(['python', mbed, 'import', test1, 'testimport'])

    assertls(mbed, 'testimport', [
        "testimport",
        "|- test2",
        "|  `- test3",
        "|     `- test4",
        "`- test3",
        "   `- test4",
    ])
