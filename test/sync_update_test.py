from util import *

# Tests if a 'neo sync', commit, and 'neo update' works on a simple file change
def test_sync_update(neo, testrepos):
    test1 = testrepos[0]
    popen(['python', neo, 'import', test1, 'testimport'])

    with cd('test1/test2'):
        with open('hello', 'w') as f:
            f.write('hello\n')
        popen([scm(), 'add', 'hello'])
        popen(['python', neo, 'sync'])
        mkcommit()

    with cd('test1'):
        popen(['python', neo, 'sync'])
        mkcommit()

    with cd('testimport'):
        popen(['python', neo, 'update'])

    assert os.path.isfile('testimport/test2/hello')

# Tests if removing a library is carried over sync/update
def test_sync_update_remove(neo, testrepos):
    test1 = testrepos[0]
    popen(['python', neo, 'import', test1, 'testimport'])

    with cd('test1/test2'):
        remove('test3')
        popen(['python', neo, 'sync'])
        mkcommit()

    with cd('test1'):
        popen(['python', neo, 'sync'])
        mkcommit()

    with cd('testimport'):
        popen(['python', neo, 'update'])

    assertls(neo, 'testimport', [
        "testimport",
        "`- test2",
    ])

# Tests if adding a library is carried over sync/update
def test_sync_update_add(neo, testrepos):
    test1 = testrepos[0]
    test3 = testrepos[2]
    popen(['python', neo, 'import', test1, 'testimport'])

    with cd('test1/test2'):
        copy('test3', 'testcopy')
        popen(['python', neo, 'sync'])
        mkcommit()

    with cd('test1'):
        popen(['python', neo, 'sync'])
        mkcommit()

    with cd('testimport'):
        popen(['python', neo, 'update'])

    assertls(neo, 'testimport', [
        "testimport",
        "`- test2",
        "   |- test3",
        "   |  `- test4",
        "   `- testcopy",
        "      `- test4",
    ])

# Tests if moving a library is carried over sync/update
def test_sync_update_move(neo, testrepos):
    test1 = testrepos[0]
    test3 = testrepos[2]
    popen(['python', neo, 'import', test1, 'testimport'])

    with cd('test1/test2'):
        move('test3', 'testmove')
        popen(['python', neo, 'sync'])
        mkcommit()

    with cd('test1'):
        popen(['python', neo, 'sync'])
        mkcommit()

    with cd('testimport'):
        popen(['python', neo, 'update'])

    assertls(neo, 'testimport', [
        "testimport",
        "`- test2",
        "   `- testmove",
        "      `- test4",
    ])

