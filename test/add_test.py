from util import *

def test_add(neo, teststructure):
    test3 = teststructure[2]

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

def test_import_after_add(neo, teststructure):
    test_add(neo, teststructure)
    mkcommit('test1')

    test1 = teststructure[0]
    popen(['python', neo, 'import', test1, 'testimport'])

    assertls(neo, 'testimport', [
        "testimport",
        "|- test2",
        "|  `- test3",
        "|     `- test4",
        "`- test3",
        "   `- test4",
    ])
