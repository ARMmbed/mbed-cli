from util import *

def test_sync_update(neo, teststructure):
    test1 = teststructure[0]
    popen(['python', neo, 'import', test1, 'testimport'])

    with cd('test1/test2'):
        with open('hello', 'w') as f:
            f.write('hello\n')
        mkcommit('.', ['hello'])

    with cd('test1'):
        popen(['python', neo, 'sync'])
        mkcommit('.', ['test2.lib'])

    with cd('testimport'):
        popen(['python', neo, 'update'])

    assert os.path.isfile('test1/test2/hello')

