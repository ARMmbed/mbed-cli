#!/usr/bin/env python

import argparse
import sys
import re
import subprocess
import os
import contextlib
import shutil
from collections import *
from itertools import *

# Default paths to Mercurial and Git
hg_cmd = 'hg'
git_cmd = 'git'

ignores = [
    # Version control folders
    "\.hg$",
    "\.git$",
    "\.svn$",
    "\.CVS$",
    "\.cvs$",
    
    # Version control fallout
    "\.orig$",
    
    # mbed Tools
    "\.build$",
    "\.export$",
    
    # Online IDE caches
    "\.msub$",
    "\.meta$",
    "\.ctags",
    
    # uVision project files
    "\.uvproj$",
    "\.uvopt$",
    
    # Eclipse project files
    "\.project$",
    "\.cproject$",
    "\.launch$",
    
    # IAR project files
    "\.ewp$",
    "\.eww$",
    
    # GCC make
    "Makefile$",
    "Debug$",
    
    # HTML files
    "\.htm$",
    
    # Settings files
    ".settings$",
    "mbed_settings.py$",
    
    # Python 
    ".py[cod]",
    "# subrepo ignores",
    ]

# Subparser handling
parser = argparse.ArgumentParser(
    description="ARM mbed neo.py")
subparsers = parser.add_subparsers(
    title="Commands", metavar="")

# Logging and output
def message(msg):
    return "["+os.path.basename(sys.argv[0])+"] "+msg+"\n"

def log(msg):
    sys.stderr.write(message(msg))
    
def action(msg):
    sys.stderr.write(message(msg))

def error(msg, code):
    sys.stderr.write("---\n["+os.path.basename(sys.argv[0])+" ERROR] "+msg+"\n---\n")
    sys.exit(code)

def progress_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor

progress_spinner = progress_cursor()

def progress():
    sys.stdout.write(progress_spinner.next())
    sys.stdout.flush()
    sys.stdout.write('\b')

# Process handling
def subcommand(name, *args, **kwargs):
    def subcommand(command):
        subparser = subparsers.add_parser(name, **kwargs)
    
        for arg in args:
            arg = dict(arg)
            opt = arg['name']
            del arg['name']

            if isinstance(opt, basestring):
                subparser.add_argument(opt, **arg)
            else:
                subparser.add_argument(*opt, **arg)
    
        def thunk(parsed_args):
            argv = [arg['name'] for arg in args]
            argv = [(arg if isinstance(arg, basestring) else arg[-1]).strip('-')
                    for arg in argv]
            argv = {arg: vars(parsed_args)[arg] for arg in argv
                    if vars(parsed_args)[arg]}

            return command(**argv)
    
        subparser.set_defaults(command=thunk)
        return command
    return subcommand


# Process execution
class ProcessException(Exception):
    pass

def popen(command, stdin=None, **kwargs):
    # print for debugging
    log('"'+' '.join(command)+'"')
    proc = subprocess.Popen(command, **kwargs)

    if proc.wait() != 0:
        raise ProcessException(proc.returncode)

def pquery(command, stdin=None, **kwargs):
    #log("Query "+' '.join(command))
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
    stdout, _ = proc.communicate(stdin)

    if proc.returncode != 0:
        raise ProcessException(proc.returncode)

    return stdout

# Defaults config file
def set_cfg(file, var, val):
    try:
        with open(file) as f:
            lines = f.read().splitlines()
    except:
        lines = []

    for line in lines:
        m = re.match('^([\w+-]+)\=(.*)?$', line)
        if m and m.group(1) == var:
            lines.remove(line)

    lines += [var+"="+val]

    with open(file, 'w') as f:
        f.write('\n'.join(lines) + '\n')

def get_cfg(file, var):
    try:
        with open(file) as f:
            lines = f.read().splitlines()
    except:
        lines = []

    for line in lines:
        m = re.match('^([\w+-]+)\=(.*)?$', line)
        if m and m.group(1) == var:
            return m.group(2)
    
# Directory navigation
@contextlib.contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(newdir)
    try:
        yield
    finally:
        os.chdir(prevdir)

def relpath(root, path):
    return path[len(root)+1:]

# Handling for multiple version controls
scms = {}
def scm(name):
    def scm(cls):
        scms[name] = cls()
        return cls
    return scm

def staticclass(cls):
    for k, v in cls.__dict__.items():
        if hasattr(v, '__call__') and not k.startswith('__'):
            setattr(cls, k, staticmethod(v))

    return cls

    
@scm('hg')
@staticclass
class Hg(object):
    name = 'hg'
    store = '.hg'

    def isurl(url):
        return re.match('^https?\:\/\/(developer\.)?mbed\.(org|com)', url)

    def clone(url, name=None, hash=None):
        action("Cloning "+name+" from "+url)
        popen([hg_cmd, 'clone', url, name] + (['-u', hash] if hash else []))

    def add(file):
        action("Adding "+file)
        try:
            popen([hg_cmd, 'add', file])
        except ProcessException:
            pass
        
    def remove(file):
        action("Removing "+file)
        try:
            popen([hg_cmd, 'rm', '-f', file])
        except ProcessException:
            pass
        try:
            os.remove(file)
        except OSError:
            pass

    def commit():
        popen([hg_cmd, 'commit'])
        
    def push():
        action("Pushing to remote repository")
        popen([hg_cmd, 'push'])
        
    def pull():
        action("Pulling from remote repository")
        popen([hg_cmd, 'pull'])

    def update(hash=None, clean=False):
        action("Updating repository to %s" % ("revision "+hash if hash else "latest revision in the current branch"))
        popen([hg_cmd, 'update'] + (['-r', hash] if hash else []) + (['-C'] if clean else []))

    def status():
        popen([hg_cmd, 'status'])

    def dirty():
        return pquery([hg_cmd, 'status', '-q'])
       
    def outgoing():
        return pquery([hg_cmd, 'outgoing'])
        
    def geturl(repo):
        tagpaths = '[paths]'
        default_url = ''
        url = ''
        with open(os.path.join(repo.path, '.hg/hgrc')) as f: 
            lines = f.read().splitlines()
            if tagpaths in lines:
                idx = lines.index(tagpaths)
                m = re.match('^([\w_]+)\s*=\s*(.*)?$', lines[idx+1])
                if m:
                    if m.group(1) == 'default':
                        default_url = m.group(2)
                    else:
                        url = m.group(2)

        if default_url:
            url = default_url
        return url if url else pquery([hg_cmd, 'paths', 'default']).strip()

    def gethash(repo):
        with open(os.path.join(repo.path, '.hg/dirstate'), 'rb') as f:
            return ''.join('%02x'%ord(i) for i in f.read(6))
            
    def ignores(repo):
        hook = 'ignore.local = .hg/hgignore'
        with open(os.path.join(repo.path, '.hg/hgrc')) as f:
            if hook not in f.read().splitlines():
                with open('.hg/hgrc', 'a') as f:
                    f.write('[ui]\n')
                    f.write(hook + '\n')

        exclude = os.path.join(repo.path, '.hg/hgignore')
        with open(exclude, 'w') as f:
            f.write("syntax: regexp\n"+'\n'.join(ignores)+'\n')

    def ignore(repo, file):
        hook = 'ignore.local = .hg/hgignore'
        with open(os.path.join(repo.path, '.hg/hgrc')) as f:
            if hook not in f.read().splitlines():
                with open('.hg/hgrc', 'a') as f:
                    f.write('[ui]\n')
                    f.write(hook + '\n')

        file = '^%s/' % file
        exclude = os.path.join(repo.path, '.hg/hgignore')
        try: 
            with open(exclude) as f:
                exists = file in f.read().splitlines()
        except IOError:
            exists = False

        if not exists:
            with open(exclude, 'a') as f:
                f.write(file + '\n')

    def unignore(repo, file):
        file = '^%s/' % file
        exclude = os.path.join(repo.path, '.hg/hgignore')
        try:
            with open(exclude) as f:
                lines = f.read().splitlines()
        except:
            lines = ''

        if file not in lines:
            return

        lines.remove(file)

        with open(exclude, 'w') as f:
            f.write('\n'.join(lines) + '\n')

            
@scm('git')
@staticclass
class Git(object):
    name = 'git'
    store = '.git'

    def isurl(url):
        return re.match('\.git$', url) or re.match('^https?\:\/\/github\.com', url)

    def clone(url, name=None, hash=None):
        action("Cloning "+name+" from "+url)
        popen([git_cmd, 'clone', url, name])
        if hash:
            with cd(name):
                popen([git_cmd, 'checkout', '-q', hash])

    def add(file):
        action("Adding "+file)
        try:
            popen([git_cmd, 'add', file])
        except ProcessException:
            pass
        
    def remove(file):
        action("Removing "+file)
        try:
            popen([git_cmd, 'rm', '-f', file])
        except ProcessException:
            pass
        try:
            os.remove(file)
        except OSError:
            pass

    def commit():
        popen([git_cmd, 'commit', '-a'])
        
    def push():
        action("Pushing to remote repository")
        popen([git_cmd, 'push', '--all'])
        
    def pull():
        action("Pulling from remote repository")
        popen([git_cmd, 'fetch', 'origin'])

    def update(hash=None, clean=False):
        action("Updating repository to %s" % ("revision "+hash if hash else "latest revision in the current branch"))
        if clean:
            popen([git_cmd, 'reset', '--hard'])

        if hash:
            popen([git_cmd, 'checkout'] + [hash])
        else:
            popen([git_cmd, 'merge'] + ['origin/master'])

    def status():
        popen([git_cmd, 'status', '-s'])
        
    def dirty():
        return pquery([git_cmd, 'diff', '--name-only', 'HEAD'])

    def outgoing():
        try:
            pquery([git_cmd, 'log', 'origin..'])
            return True
        except ProcessException as e:
            if e[0] != 1:
                raise
            return False

    def geturl(repo):
        return pquery([git_cmd, 'config', '--get', 'remote.origin.url']).strip()

    def gethash(repo):
        return pquery([git_cmd, 'rev-parse', '--short', 'HEAD']).strip()

    def ignores(repo):
        with open(os.path.join(repo.path, '.git/info/exclude'), 'w') as f:
            f.write('\n'.join(ignores)+'\n')

    def ignore(repo, file):
        exclude = os.path.join(repo.path, '.git/info/exclude')
        try: 
            with open(exclude) as f:
                exists = file in f.read().splitlines()
        except IOError:
            exists = False

        if not exists:
            with open(exclude, 'a') as f:
                f.write(file + '\n')

    def unignore(repo, file):
        exclude = os.path.join(repo.path, '.git/info/exclude')
        try:
            with open(exclude) as f:
                lines = f.read().splitlines()
        except:
            lines = ''

        if file not in lines:
            return

        lines.remove(file)

        with open(exclude, 'w') as f:
            f.write('\n'.join(lines) + '\n')


# Repository object
class Repo(object):
    @classmethod
    def fromurl(cls, url, path=None):
        repo = cls()

        m = re.match('^(.*/([\w+-]+)(?:\.\w+)?)/?(?:#(.*))?$', url.strip())
        if not m:
            error('Invalid repository (%s)' % url.strip(), -1)

        repo.name = os.path.basename(path or m.group(2))
        repo.path = os.path.abspath(path or os.path.join(os.getcwd(), repo.name))

        repo.url = m.group(1)
        repo.hash = m.group(3)
        return repo

    @classmethod
    def fromlib(cls, lib=None):
        assert lib.endswith('.lib')
        with open(lib) as f:
            return cls.fromurl(f.read(), lib[:-4])

    @classmethod
    def fromrepo(cls, path=None):
        repo = cls()
        if path is None:
            path = Repo.findrepo(os.getcwd())
            if path is None:
                error('Cannot find the root repository. Hint: use "git init" or "hg init" to create one.', 1)

        repo.path = os.path.abspath(path)
        repo.name = os.path.basename(repo.path)

        repo.sync()

        if repo.scm is None:
            error("Current folder is not a supported repository", -1)

        return repo

    @classmethod
    def isrepo(cls, path=None):
        for name, scm in scms.items():
            if os.path.isdir(os.path.join(path, '.'+name)):
                return True
        return False
        
    @classmethod
    def findrepo(cls, path=None):
        path = path or os.getcwd()

        while cd(path):
            if Repo.isrepo(path):
                return path

            tpath = path
            path = os.path.split(path)[0]
            if tpath == path:
                break

        return None

    @property
    def lib(self):
        return self.path + '.lib'

    @property
    def fullurl(self):
        if self.url:
            return (self.url.rstrip('/') + '/' +
                ('#'+self.hash if self.hash else ''))

    def sync(self):
        if os.path.isdir(self.path):
            try:
                self.scm = self.getscm()
            except ProcessException:
                pass

            try:
                self.url = self.geturl()
            except ProcessException:
                pass

            try:
                self.hash = self.gethash()
            except ProcessException:
                pass

            try:
                self.libs = list(self.getlibs())
            except ProcessException:
                pass

    def getscm(self):
        for name, scm in scms.items():
            if os.path.isdir(os.path.join(self.path, '.'+name)):
                return scm

    def gethash(self):
        if self.scm:
            with cd(self.path):
                return self.scm.gethash(self)

    def geturl(self):
        if self.scm:
            with cd(self.path):
                return self.scm.geturl(self)

    def getlibs(self):
        for root, dirs, files in os.walk(self.path):
            dirs[:]  = [d for d in dirs  if not d.startswith('.')]
            files[:] = [f for f in files if not f.startswith('.')]

            for file in files:
                if file.endswith('.lib'):
                    yield Repo.fromlib(os.path.join(root, file))
                    if file[:-4] in dirs:
                        dirs.remove(file[:-4])

    def write(self):
        if os.path.isfile(self.lib):
            with open(self.lib) as f:
                if f.read().strip() == self.fullurl.strip():
                    #print self.name, 'unmodified'
                    progress()
                    return

        with open(self.lib, 'wb') as f:
            f.write(self.fullurl + '\n')

        print self.name, '->', self.fullurl

        
# Clone command
@subcommand('import', 
    dict(name='url', help='URL of the program'),
    dict(name='path', nargs='?', help='Destination local path'),
    help='Import a program into the current directory')
def import_(url, path=None):
    repo = Repo.fromurl(url, path)

    # Sorted so repositories that match urls are attempted first
    sorted_scms = [(scm.isurl(url), scm) for scm in scms.values()]
    sorted_scms = sorted(sorted_scms, key=lambda (m, _): not m)

    for _, scm in sorted_scms:
        try:
            scm.clone(repo.url, repo.path, repo.hash)
            break
        except ProcessException:
            pass

    repo.sync()

    with cd(repo.path):
        deploy()


# Deploy command
@subcommand('deploy',
    help='Import dependencies in the current program or library')
def deploy():
    repo = Repo.fromrepo()
    repo.scm.ignores(repo)

    for lib in repo.libs:
        import_(lib.fullurl, lib.path)
        repo.scm.ignore(repo, relpath(repo.path, lib.path))

    # This has to be replaced by one time python script from tools that sets up everything the developer needs to use the tools
    if (not os.path.isfile('mbed_settings.py') and 
        os.path.isfile('mbed-os/tools/default_settings.py')):
        shutil.copy('mbed-os/tools/default_settings.py', 'mbed_settings.py')

        
# Install/uninstall command
@subcommand('add', 
    dict(name='url', help="URL of the library"),
    dict(name='path', nargs='?', help="Destination local path"),
    help='Add a library and its dependencies to the current directory')
def add(url, path=None):
    repo = Repo.fromrepo()

    lib = Repo.fromurl(url, path)
    import_(lib.url, lib.path)
    repo.scm.ignore(repo, relpath(repo.path, lib.path))
    lib.sync()

    lib.write()
    repo.scm.add(lib.lib)

    
@subcommand('remove', 
    dict(name='path', help="Local library name or path"),
    help='Remove a library and its dependencies from the current directory')
def remove(path):
    repo = Repo.fromrepo()
    if not Repo.isrepo(path):
        error("Could not find library in path (%s)" % path, 1)

    lib = Repo.fromrepo(path)

    repo.scm.remove(lib.lib)
    shutil.rmtree(lib.path)
    repo.scm.unignore(repo, relpath(repo.path, lib.path))

    
# Publish command
@subcommand('publish',
    help='Publish program or library and its dependencies from the current directory')
def publish(top=True):
    if top:
        action("Checking for modifications...")

    repo = Repo.fromrepo()
    for lib in repo.libs:
        with cd(lib.path):
            progress()
            publish(False)

    sync(recursive=False)
    dirty = repo.scm.dirty()

    if dirty:
        action('Uncommitted changes in %s (%s)' % (repo.name, repo.path))
        raw_input('Press enter to commit and push: ')
        repo.scm.commit()

    try:
        if repo.scm.outgoing():
            repo.scm.push()
    except ProcessException as e:
        if e[0] != 1:
            raise

            
# Update command
@subcommand('update',
    dict(name='rev', nargs='?', help="Revision hash or branch"),
    dict(name=['-C', '--clean'], action="store_true", help="Perform a clean update and discard all local changes"),
    help='Update program or library and its dependencies in the current directory')
def update(rev=None,clean=False):
    repo = Repo.fromrepo()
    repo.scm.pull()
    repo.scm.update(rev,clean=clean)

    for lib in repo.libs:
        if (not os.path.isfile(lib.lib) or 
            (Repo.isrepo(lib.path) and lib.fullurl != Repo.fromrepo(lib.path).fullurl)):
            if not clean and Repo.isrepo(lib.path):
                with cd(lib.path):
                    if Repo.fromrepo(lib.path).scm.dirty():
                        error('Uncommitted changes in %s (%s)\n'
                            % (lib.name, lib.path), 1)

            shutil.rmtree(lib.path)
            repo.scm.unignore(repo, relpath(repo.path, lib.path))

    repo.sync()

    for lib in repo.libs:
        if os.path.isdir(lib.path):
            with cd(lib.path):
                update(lib.hash)
        else:
            import_(lib.url, lib.path)
            repo.scm.ignore(repo, relpath(repo.path, lib.path))

            
# Synch command
@subcommand('sync',
    help='Synchronize dependency references (.lib files)')
def sync(recursive=True, top=True):
    if top and recursive:
        action("Synchronizing dependency references...")
        
    repo = Repo.fromrepo()
    repo.scm.ignores(repo)

    for lib in repo.libs:
        if os.path.isdir(lib.path):
            lib.sync()
            lib.write()
            repo.scm.ignore(repo, relpath(repo.path, lib.path))
        else:
            repo.scm.remove(lib.lib)
            repo.scm.unignore(repo, relpath(repo.path, lib.path))

    for root, dirs, files in os.walk(repo.path):
        dirs[:]  = [d for d in dirs  if not d.startswith('.')]
        files[:] = [f for f in files if not f.startswith('.')]

        for dir in list(dirs):
            if not Repo.isrepo(os.path.join(root, dir)):
                continue

            lib = Repo.fromrepo(os.path.join(root, dir))            
            if os.path.isfile(lib.lib):
                dirs.remove(dir)
                continue

            dirs.remove(dir)
            lib.write()
            repo.scm.ignore(repo, relpath(repo.path, lib.path))
            repo.scm.add(lib.lib)

    repo.sync()

    if recursive:
        for lib in repo.libs:
            with cd(lib.path):
                sync(top=False)

            
@subcommand('ls',
    dict(name=['-a', '--all'], action='store_true', help="List repository URL and hash pairs"),
    help='View program or library tree.')
def list_(all=False, prefix=''):
    repo = Repo.fromrepo()
    print prefix + repo.name, '(%s)' % (repo.url if all else repo.hash)

    for i, lib in enumerate(repo.libs):
        if prefix:
            nprefix = prefix[:-3] + ('|  ' if prefix[-3] == '|' else '   ')
        else:
            nprefix = ''

        nprefix += '|- ' if i < len(repo.libs)-1 else '`- '

        with cd(lib.path):
            list_(all, nprefix)

            
@subcommand('status',
    help='Show status of program or library and its dependencies in the current directory')
def status():
    repo = Repo.fromrepo()
    if repo.scm.dirty():
        print '---', repo.name, '---'
        repo.scm.status()

    for lib in repo.libs:
        with cd(lib.path):
            status()

            
@subcommand('compile',
    dict(name=['-t', '--toolchain'], help="Compile toolchain. Example: ARM, uARM, GCC_ARM, IAR"),
    dict(name=['-m', '--mcu'], help="Compile target. Example: K64F, NUCLEO_F401RE, NRF51822..."),
    help='Compile program using the native mbed OS build system')
def compile(toolchain=None, mcu=None):
    if not os.path.isdir('mbed-os'):
        error('mbed-os not found?\n', -1)

    args = remainder
    repo = Repo.fromrepo()
    file = os.path.join(repo.scm.store, 'neo')

    target = mcu if mcu else get_cfg(file, 'TARGET')
    if target is None:
        error('Please specify compile target using the -m switch or set default target using command "target"', 1)
        
    tchain = toolchain if toolchain else get_cfg(file, 'TOOLCHAIN')
    if tchain is None:
        error('Please specify compile toolchain using the -t switch or set default toolchain using command "toolchain"', 1)

    macros = []
    if os.path.isfile('MACROS.txt'):
        with open('MACROS.txt') as f:
            macros = f.read().splitlines()

    env = os.environ.copy()
    env['PYTHONPATH'] = '.'
    popen(['python', 'mbed-os/tools/make.py']
        + list(chain.from_iterable(izip(repeat('-D'), macros)))
        + ['-t', tchain, '-m', target,
           '--source=.',
           '--build=%s' % os.path.join('.build', target, tchain)]
        + args,
        env=env)

        
# Export command
@subcommand('export',
    dict(name=['-i', '--ide'], help="IDE to create project files for. Example: UVISION,DS5,IAR", required=True),
    dict(name=['-m', '--mcu'], help="Export for target MCU. Example: K64F, NUCLEO_F401RE, NRF51822..."),
    help='Generate project files for desktop IDEs')
def export(ide=None, mcu=None):
    if not os.path.isdir('mbed-os'):
        error('mbed-os not found?\n', -1)

    args = remainder
    repo = Repo.fromrepo()
    file = os.path.join(repo.scm.store, 'neo')
    
    target = mcu if mcu else get_cfg(file, 'TARGET')
    if target is None:
        error('Please specify export target using the -m switch or set default target using command "target"', 1)

    macros = []
    if os.path.isfile('MACROS.txt'):
        with open('MACROS.txt') as f:
            macros = f.read().splitlines()

    env = os.environ.copy()
    env['PYTHONPATH'] = '.'
    popen(['python', 'mbed-os/tools/project.py']
        + list(chain.from_iterable(izip(repeat('-D'), macros)))
        + ['-m', target, '--source=%s' % repo.path]
        + args,
        env=env)

        
# Build system and exporters
@subcommand('target',
    dict(name='name', nargs='?', help="Default target name. Example: K64F, NUCLEO_F401RE, NRF51822..."),
    help='Set default target when compiling and exporting')
def target(name=None):
    repo = Repo.fromrepo()
    
    file = os.path.join(repo.scm.store, 'neo')
    if name is None:
        name = get_cfg(file, 'TARGET')
        if name:
            action('The current target for this program is "%s"' % name)
        else:
            action('No target is specified for this program')
    else:        
        set_cfg(file, 'TARGET', name)
        action('"%s" now set as default target' % name)

    
@subcommand('toolchain',
    dict(name='name', nargs='?', help="Default toolchain name. Example: ARM, uARM, GCC_ARM, IAR"),
    help='Sets default toolchain')
def toolchain(name=None):
    repo = Repo.fromrepo()
    
    file = os.path.join(repo.scm.store, 'neo')
    if name is None:
        name = get_cfg(file, 'TOOLCHAIN')
        if name:
            action('The current toolchain for this program is "%s"' % name)
        else:
            action('No toolchain is specified for this program')
    else:
        set_cfg(file, 'TOOLCHAIN', name)
        action('"%s" now set as default toolchain' % name)


# Parse/run command
if len(sys.argv) <= 1:
    parser.print_help()
    sys.exit(1)

args, remainder = parser.parse_known_args()

try:
    status = args.command(args)
except ProcessException as e:
    error('Process exit with error code %d' % e[0], e[0])
except KeyboardInterrupt as e:
    error('User aborted!', 255)

sys.exit(status or 0)
