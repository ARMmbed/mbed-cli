#!/usr/bin/env python

import argparse
import sys
import re
import subprocess
import os
import contextlib
import shutil
import stat
from collections import *
from itertools import *


# Default paths to Mercurial and Git
hg_cmd = 'hg'
git_cmd = 'git'

ignores = [
    # Version control folders
    ".hg",
    ".git",
    ".svn",
    ".CVS",
    ".cvs",
    
    # Version control fallout
    "*.orig",
    
    # mbed Tools
    ".build",
    ".export",
    
    # Online IDE caches
    ".msub$",
    ".meta$",
    ".ctags*",
    
    # uVision project files
    "*.uvproj",
    "*.uvopt",
    
    # Eclipse project files
    "*.project",
    "*.cproject",
    "*.launch",
    
    # IAR project files
    "*.ewp",
    "*.eww",
    
    # GCC make
    "Makefile",
    "Debug",
    
    # HTML files
    "*.htm",
    
    # Settings files
    "*.settings",
    "mbed_settings.py",
    
    # Python 
    "*.py[cod]",
    "# subrepo ignores",
    ]

regex_git_url = '^(git@|git\://|ssh\://|https?\://)([^/:]+)[:/](.+?)(\.git|\/?)$'
regex_hg_url = '^(file|ssh|https?)://([^/:]+)/([^/]+)/?([^/]+?)?$'
regex_mbed_url = '^(https?)://([\w\-\.]*mbed\.(co\.uk|org|com))/(users|teams)/([\w\-]{1,32})/(repos|code)/([\w\-]+)/?$'

# Logging and output
def message(msg):
    return "[mbed] %s\n" % msg

def log(msg):
    sys.stderr.write(message(msg))
    
def action(msg):
    sys.stderr.write(message(msg))

def warning(msg, code):
    for line in msg.splitlines():
        sys.stderr.write("[mbed WARNING] %s\n" % line)
    sys.stderr.write("---\n")

def error(msg, code):
    for line in msg.splitlines():
        sys.stderr.write("[mbed ERROR] %s\n" % line)
    sys.stderr.write("---\n")
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
    #log("Query "+' '.join(command)+" in "+os.getcwd())
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
    stdout, _ = proc.communicate(stdin)

    if proc.returncode != 0:
        raise ProcessException(proc.returncode)

    return stdout

def rmtree_readonly(directory):
    def remove_readonly(func, path, _):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    shutil.rmtree(directory, onerror=remove_readonly)


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

def get_cfg(file, var, default_val=None):
    try:
        with open(file) as f:
            lines = f.read().splitlines()
    except:
        lines = []

    for line in lines:
        m = re.match('^([\w+-]+)\=(.*)?$', line)
        if m and m.group(1) == var:
            return m.group(2)
    return default_val


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


def staticclass(cls):
    for k, v in cls.__dict__.items():
        if hasattr(v, '__call__') and not k.startswith('__'):
            setattr(cls, k, staticmethod(v))

    return cls


# Handling for multiple version controls
scms = {}
def scm(name):
    def scm(cls):
        scms[name] = cls()
        return cls
    return scm

@scm('hg')
@staticclass
class Hg(object):
    name = 'hg'
    store = '.hg'

    def isurl(url):
        return re.match('^https?\:\/\/(developer\.)?mbed\.(org|com)', url)

    def init(path=None):
        action("Initializing repository")
        popen([hg_cmd, 'init'] + ([path] if path else []))

    def clone(url, name=None, hash=None, depth=None, protocol=None):
        action("Cloning "+name+" from "+url)
        popen([hg_cmd, 'clone', formaturl(url, protocol), name] + (['-u', hash] if hash else []))

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
        
    def push(repo):
        action("Pushing local repository \"%s\" to remote \"%s\"" % (repo.name, repo.url))
        popen([hg_cmd, 'push'])
        
    def pull(repo):
        action("Pulling remote repository \"%s\" to local \"%s\"" % (repo.url, repo.name))
        popen([hg_cmd, 'pull'])

    def update(repo, hash=None, clean=False):
        action("Pulling remote repository \"%s\" to local \"%s\"" % (repo.url, repo.name))
        popen([hg_cmd, 'pull'])
        action("Updating \"%s\" to %s" % (repo.name, "revision "+hash if hash else "latest revision in the current branch"))
        popen([hg_cmd, 'update'] + (['-r', hash] if hash else []) + (['-C'] if clean else []))

    def status():
        return pquery([hg_cmd, 'status'])

    def dirty():
        return pquery([hg_cmd, 'status', '-q'])

    def untracked():
        result = pquery([hg_cmd, 'status', '-u'])
        return re.sub('^\? ', '', result).splitlines()

    def outgoing():
        try:
            pquery([hg_cmd, 'outgoing'])
            return True
        except ProcessException as e:
            if e[0] != 1:
                raise
            return False

    def isdetached():
        return False

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
        return formaturl(url or pquery([hg_cmd, 'paths', 'default']).strip())

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
            f.write("syntax: glob\n"+'\n'.join(ignores)+'\n')

    def ignore(repo, file):
        hook = 'ignore.local = .hg/hgignore'
        with open(os.path.join(repo.path, '.hg/hgrc')) as f:
            if hook not in f.read().splitlines():
                with open('.hg/hgrc', 'a') as f:
                    f.write('[ui]\n')
                    f.write(hook + '\n')

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

    def init(path=None):
        action("Initializing repository")
        popen([git_cmd, 'init'] + ([path] if path else []))

    def clone(url, name=None, hash=None, depth=None, protocol=None):
        action("Cloning "+name+" from "+url)
        popen([git_cmd, 'clone', formaturl(url, protocol), name] + (['--depth', depth] if depth else []))
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
        
    def push(repo):
        action("Pushing local repository \"%s\" to remote \"%s\"" % (repo.name, repo.url))
        popen([git_cmd, 'push', '--all'])
        
    def pull(repo):
        action("Pulling remote repository \"%s\" to local \"%s\"" % (repo.url, repo.name))
        popen([git_cmd, 'fetch', '--all'])

    def update(repo, hash=None, clean=False):
        if clean:
            action("Discarding local changes in \"%s\"" % repo.name)
            popen([git_cmd, 'reset', '--hard'])
        if hash:
            action("Fetching remote repository \"%s\" to local \"%s\"" % (repo.url, repo.name))
            popen([git_cmd, 'fetch', '-v', '--all'])
            action("Updating \"%s\" to %s" % (repo.name, hash))
            popen([git_cmd, 'checkout'] + [hash])
        else:
            action("Fetching remote repository \"%s\" to local \"%s\" and updating to latest revision in the current branch" % (repo.url, repo.name))
            popen([git_cmd, 'pull', '-v', '--all'])

    def status():
        return pquery([git_cmd, 'status', '-s'])
        
    def dirty():
        return pquery([git_cmd, 'diff', '--name-only', 'HEAD'])

    def untracked():
        return pquery([git_cmd, 'ls-files', '--others', '--exclude-standard']).splitlines()

    def outgoing():
        try:
            return True if pquery([git_cmd, 'log', 'origin..']) else False
        except ProcessException as e:
            if e[0] != 1:
                raise
            return True

    def isdetached():
        branch = pquery([git_cmd, 'rev-parse', '--symbolic-full-name', '--abbrev-ref', 'HEAD']).strip()
        return branch == "HEAD"

    def geturl(repo):
        url = ""
        remotes = pquery([git_cmd, 'remote', '-v']).strip().splitlines()
        for remote in remotes:
            remote = re.split("\s", remote)
            if "(fetch)" in remote:
                url = remote[1]
                if remote[0] == "origin": # Prefer origin URL
                    break
        return formaturl(url)

    def gethash(repo):
        return pquery([git_cmd, 'rev-parse', 'HEAD']).strip()

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
                f.write(file.replace("\\", "/") + '\n')

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
    is_local = False
    
    @classmethod
    def fromurl(cls, url, path=None):
        repo = cls()
        m_local = re.match('^([\w.+-][\w./+-]+)/?(?:#(.*))?$', url.strip().replace('\\', '/'))
        m_url = re.match('^(.*/([\w+-]+)(?:\.\w+)?)/?(?:#(.*))?$', url.strip().replace('\\', '/'))
        if m_local:
            repo.name = os.path.basename(path or m_local.group(1))
            repo.path = os.path.abspath(path or os.path.join(os.getcwd(), m_local.group(1)))
            repo.url = m_local.group(1)
            repo.hash = m_local.group(2)
            repo.is_local = True
        elif m_url:
            repo.name = os.path.basename(path or m_url.group(2))
            repo.path = os.path.abspath(path or os.path.join(os.getcwd(), repo.name))
            repo.url = formaturl(m_url.group(1))
            repo.hash = m_url.group(3)
        else:
            error('Invalid repository (%s)' % url.strip(), -1)
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
                error('Cannot find the program or library in the current path \"%s\".\nPlease change your working directory to a different location or use command \"new\" to create a new program.' % os.getcwd(), 1)

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
        else:
            return False
            
        return False

    @classmethod
    def findrepo(cls, path=None):
        path = os.path.abspath(path or os.getcwd())

        while cd(path):
            if Repo.isrepo(path):
                return path

            tpath = path
            path = os.path.split(path)[0]
            if tpath == path:
                break

        return None

    @classmethod
    def findroot(cls, path=None):
        path = os.path.abspath(path or os.getcwd())
        rpath = None

        while cd(path):
            tpath = path
            path = Repo.findrepo(path)
            if path:
                rpath = path
                path = os.path.split(path)[0]
                if tpath == path:       # Reached root.
                    break
            else:
                break

        return rpath

    @classmethod
    def typerepo(cls, path=None):
        path = os.path.abspath(path or os.getcwd())

        depth = 0
        while cd(path):
            tpath = path
            path = Repo.findrepo(path)
            if path:
                depth += 1
                path = os.path.split(path)[0]
                if tpath == path:       # Reached root.
                    break
            else:
                break

        return "directory" if depth == 0 else ("program" if depth == 1 else "library")

    @property
    def lib(self):
        return self.path + '.lib'

    @property
    def fullurl(self):
        if self.url:
            return (self.url.rstrip('/') + '/' +
                ('#'+self.hash if self.hash else ''))

    def sync(self):
        self.url = None
        self.hash = None
        if os.path.isdir(self.path):
            try:
                self.scm = self.getscm()
            except ProcessException:
                pass

            try:
                self.url = self.geturl()
                if not self.url:
                    self.is_local = True
                    ppath = self.findrepo(os.path.split(self.path)[0])
                    self.url = relpath(ppath, self.path).replace("\\", "/") if ppath else os.path.basename(self.path)
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
                return self.scm.geturl(self).strip().replace('\\', '/')

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

        action("Update reference \"%s\" -> \"%s\"" % (self.name, self.fullurl))

    def rm_untracked(self):
        untracked = self.scm.untracked()
        for file in untracked:
            if re.match("(.+)\.lib$", file) and os.path.isfile(file):
                action("Remove untracked library reference \"%s\"" % file)
                os.remove(file)

                
def formaturl(url, format="default"):
    url = "%s" % url
    m = re.match(regex_mbed_url, url)
    if m:
        url = 'https://mbed.org/'+m.group(4)+'/'+m.group(5)+'/code/'+m.group(7)
    else:
        m = re.match(regex_git_url, url)
        if m:
            if format == "ssh":
                url = 'ssh://%s/%s.git' % (m.group(2), m.group(3))
            elif format == "http":
                url = 'http://%s/%s' % (m.group(2), m.group(3))
            else:
                url = 'https://%s/%s' % (m.group(2), m.group(3)) # https is default
        else:
            m = re.match(regex_hg_url, url)
            if m:
                if format == "ssh":
                    url = 'ssh://%s/%s' % (m.group(2), m.group(3))
                elif format == "http":
                    url = 'http://%s/%s' % (m.group(2), m.group(3))
                else:
                    url = 'https://%s/%s' % (m.group(2), m.group(3)) # https is default
    return url


# Help messages adapt based on current dir
cwd_type = Repo.typerepo()
cwd_dest = "program" if cwd_type == "directory" else "library"


# Subparser handling
parser = argparse.ArgumentParser(description="A command-line code management tool for ARM mbed OS - http://www.mbed.com\nmbed uses current directory as a working context.")
subparsers = parser.add_subparsers(title="Commands", metavar="           ")

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


# Clone command
@subcommand('new', 
    dict(name='scm', help='Source control management. Currently supported: %s' % ', '.join([s.name for s in scms.values()])),
    dict(name='path', nargs='?', help='Destination name or path. Default: current folder.'),
    help='Create a new program based on the specified source control management. Will create a new library when called from inside a local program. Supported SCMs: %s.' % (', '.join([s.name for s in scms.values()])))
def new(scm, path=None):
    repo_scm = [s for s in scms.values() if s.name == scm.lower()]
    if not repo_scm:
        error("Please specify one of the following source control management systems: %s" % ', '.join([s.name for s in scms.values()]), 1)

    d_path = path or os.getcwd()
    if os.path.isdir(d_path) and len(os.listdir(d_path)) > 1:
        error("Directory \"%s\" is not empty. Please select different path or manually remove all files." % d_path, 1)

    if Repo.isrepo(d_path):
        error("A %s is already initialized in \"%s\". Please select different path or manually remove all files." % (cwd_dest, d_path), 1)

    p_path = Repo.findrepo(path)    # Find parent repository
    repo_scm[0].init(d_path)        # Initialize repository
    
    if p_path:  # It's a library
        with cd(p_path):
            sync()
    else:       # It's a program. Add mbed-os
        with cd(d_path):
            add("https://github.com/ARMmbed/mbed-os")
        if path:
            os.chdir(path)


# Clone command
@subcommand('import', 
    dict(name='url', help='URL of the %s' % cwd_dest),
    dict(name='path', nargs='?', help='Destination name or path. Default: current %s.' % cwd_type),
    dict(name='--depth', nargs='?', help='Number of revisions to fetch from the remote repository. Default: all revisions.'),
    dict(name='--protocol', nargs='?', help='Transport protocol for the source control management. Supported: https, http, ssh, git. Default: inferred from URL.'),
    help='Import a program and its dependencies into the current directory or specified destination path.')
def import_(url, path=None, top=True, depth=None, protocol=None):
    repo = Repo.fromurl(url, path)

    if top and cwd_type != "directory":
        d_path = os.path.abspath(path or os.getcwd())
        error("Cannot import program in the specified location \"%s\" because it's already part of a program.\nPlease change your working directory to a different location or use command \"add\" to import the URL as a library." % d_path, 1)

    # Sorted so repositories that match urls are attempted first
    sorted_scms = [(scm.isurl(url), scm) for scm in scms.values()]
    sorted_scms = sorted(sorted_scms, key=lambda (m, _): not m)

    for _, scm in sorted_scms:
        try:
            scm.clone(repo.url, repo.path, repo.hash, depth=depth, protocol=protocol)
            break
        except ProcessException:
            pass
    else:
        error("Unable to clone repository (%s)" % url, 1)

    repo.sync()

    with cd(repo.path):
        deploy(depth=depth, protocol=protocol)

# Deploy command
@subcommand('deploy',
    dict(name='--depth', nargs='?', help='Number of revisions to fetch from the remote repository. Default: all revisions.'),
    dict(name='--protocol', nargs='?', help='Transport protocol for the source control management. Supported: https, http, ssh, git. Default: inferred from URL.'),
    help="Import missing dependencies in the current program or library.")
def deploy(depth=None, protocol=None):
    repo = Repo.fromrepo()
    repo.scm.ignores(repo)

    for lib in repo.libs:
        if not os.path.isdir(lib.path):
            import_(lib.fullurl, lib.path, top=False, depth=depth, protocol=protocol)
            repo.scm.ignore(repo, relpath(repo.path, lib.path))
        else:
            with cd(lib.path):
                deploy(depth=depth, protocol=protocol)

    # This has to be replaced by one time python script from tools that sets up everything the developer needs to use the tools
    if (not os.path.isfile('mbed_settings.py') and 
        os.path.isfile('mbed-os/tools/default_settings.py')):
        shutil.copy('mbed-os/tools/default_settings.py', 'mbed_settings.py')


# Install/uninstall command
@subcommand('add', 
    dict(name='url', help="URL of the library"),
    dict(name='path', nargs='?', help="Destination name or path. Default: current folder."),
    dict(name='--depth', nargs='?', help='Number of revisions to fetch from the remote repository. Default: all revisions.'),
    dict(name='--protocol', nargs='?', help='Transport protocol for the source control management. Supported: https, http, ssh, git. Default: inferred from URL.'),
    help='Add a library and its dependencies into the current %s or specified destination path.' % cwd_type)
def add(url, path=None, depth=None, protocol=None):
    repo = Repo.fromrepo()

    lib = Repo.fromurl(url, path)
    import_(lib.url, lib.path, top=False, depth=depth, protocol=protocol)
    repo.scm.ignore(repo, relpath(repo.path, lib.path))
    lib.sync()

    lib.write()
    repo.scm.add(lib.lib)


@subcommand('remove', 
    dict(name='path', help="Local library name or path"),
    help='Remove specified library and its dependencies from the current %s.' % cwd_type)
def remove(path):
    repo = Repo.fromrepo()
    if not Repo.isrepo(path):
        error("Could not find library in path (%s)" % path, 1)

    lib = Repo.fromrepo(path)

    repo.scm.remove(lib.lib)
    rmtree_readonly(lib.path)
    repo.scm.unignore(repo, relpath(repo.path, lib.path))


# Publish command
@subcommand('publish',
    help='Publish current %s and its dependencies to associated remote repository URLs.' % cwd_type)
def publish(top=True):
    if top:
        action("Checking for local modifications...")

    repo = Repo.fromrepo()
    if repo.is_local:
        error("%s \"%s\" in \"%s\" is a local repository.\nPlease associate it with a remote repository URL before attempting to publish.\nRead more about %s repositories here:\nhttp://developer.mbed.org/handbook/how-to-publish-with-%s/" % ("Program" if top else "Library", repo.name, repo.path, repo.scm.name, repo.scm.name), 1)

    for lib in repo.libs:
        with cd(lib.path):
            progress()
            publish(False)

    sync(recursive=False)

    if repo.scm.dirty():
        action('Uncommitted changes in %s (%s)' % (repo.name, repo.path))
        raw_input('Press enter to commit and push: ')
        repo.scm.commit()

    try:
        if repo.scm.outgoing():
            repo.scm.push(repo)
    except ProcessException as e:
        if e[0] != 1:
            raise


# Update command
@subcommand('update',
    dict(name='rev', nargs='?', help="Revision hash, tag or branch"),
    dict(name=['-C', '--clean'], action="store_true", help="Perform a clean update and discard all local changes. WARNING: This action cannot be undone. Use with caution."),
    dict(name=['-F', '--force'], action="store_true", help="Enforce the original layout and will remove any local libraries and also libraries containing uncommitted or unpublished changes. WARNING: This action cannot be undone. Use with caution."),
    dict(name=['-I', '--ignore'], action="store_true", help="Ignore errors regarding unpiblished libraries, unpublished or uncommitted changes, and attempt to update from associated remote repository URLs."),
    dict(name='--depth', nargs='?', help='Number of revisions to fetch from the remote repository. Default: all revisions.'),
    dict(name='--protocol', nargs='?', help='Transport protocol for the source control management. Supported: https, http, ssh, git. Default: inferred from URL.'),
    help='Update current %s and its dependencies from associated remote repository URLs.' % cwd_type)
def update(rev=None, clean=False, force=False, ignore=False, top=True, depth=None, protocol=None):
    def can_update(repo, clean, force):
        if (repo.is_local or repo.url is None) and not force:
            return False, "Preserving local library \"%s\" in \"%s\".\nPlease publish this library to a remote URL to be able to restore it at any time.\nYou can use --ignore switch to ignore all local libraries and update only the published ones.\nYou can also use --force switch to remove all local libraries. WARNING: This action cannot be undone." % (repo.name, repo.path)
        if not clean and repo.scm.dirty():
            return False, "Uncommitted changes in \"%s\" in \"%s\".\nPlease discard or stash them first and then retry update.\nYou can also use --clean switch to discard all uncommitted changes. WARNING: This action cannot be undone." % (repo.name, repo.path)
        if not force and repo.scm.outgoing():
            return False, "Unpublished changes in \"%s\" in \"%s\".\nPlease publish them first using the \"publish\" command.\nYou can also use --force to discard all local commits and replace the library with the one included in this revision. WARNING: This action cannot be undone." % (repo.name, repo.path)

        return True, "OK"

    if top:
        sync(keep_refs=True)
        
    repo = Repo.fromrepo()
    
    if top and not rev and repo.scm.isdetached():
        error("This %s is in detached HEAD state, and you won't be able to receive updates from the remote repository until you either checkout a branch or create a new one.\nYou can checkout a branch using \"%s checkout <branch_name>\" command before running \"mbed update\"." % (cwd_type, repo.scm.name),1)
    
    # Fetch from remote repo
    repo.scm.update(repo, rev, clean)
    repo.rm_untracked()

    # Compare library references (.lib) before and after update, and remove libraries that do not have references in the current revision
    for lib in repo.libs:
        if not os.path.isfile(lib.lib) and os.path.isdir(lib.path): # Library reference doesn't exist in the new revision. Will try to remove library to reproduce original structure
            gc = False
            with cd(lib.path):
                lib_repo = Repo.fromrepo(lib.path)
                gc, msg = can_update(lib_repo, clean, force)
            if gc:
                action("Removing leftover library \"%s\" in \"%s\"" % (lib.name, lib.path))
                rmtree_readonly(lib.path)
                repo.scm.unignore(repo, relpath(repo.path, lib.path))
            else:
                if ignore:
                    warning(msg, 1)
                else:
                    error(msg, 1)

    # Reinitialize repo.libs() to reflect the library files after update
    repo.sync()
    
    # Recheck libraries as their URLs might have changed
    for lib in repo.libs:
        if os.path.isdir(lib.path) and Repo.isrepo(lib.path):
            lib_repo = Repo.fromrepo(lib.path)
            if lib.url != lib_repo.url: # Repository URL has changed
                gc = False
                with cd(lib.path):
                    gc, msg = can_update(lib_repo, clean, force)
                if gc:
                    action("Removing library \"%s\" in \"%s\" due to changed repository URL. Will import from new URL." % (lib.name, lib.path))
                    rmtree_readonly(lib.path)
                    repo.scm.unignore(repo, relpath(repo.path, lib.path))
                else:
                    if ignore:
                        warning(msg, 1)
                    else:
                        error(msg, 1)

    # Import missing repos and update to hashes
    for lib in repo.libs:
        if not os.path.isdir(lib.path):
            import_(lib.url, lib.path, top=False, depth=depth, protocol=protocol)
            repo.scm.ignore(repo, relpath(repo.path, lib.path))
        with cd(lib.path):
            update(lib.hash, clean, force, ignore, top=False)



# Synch command
@subcommand('sync',
    help='Synchronize dependency references (.lib files) in the current %s.' % cwd_type)
def sync(recursive=True, keep_refs=False, top=True):
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
            if not keep_refs:
                action("Remove reference \"%s\" -> \"%s\"" % (lib.name, lib.fullurl))
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
            if os.path.isdir(lib.path):
                with cd(lib.path):
                    sync(keep_refs=keep_refs, top=False)

            
@subcommand('ls',
    dict(name=['-a', '--all'], action='store_true', help="List repository URL and hash pairs"),
    help='View the current %s dependency tree.' % cwd_type)
def list_(all=False, prefix=''):
    repo = Repo.fromrepo()
    print prefix + repo.name, '(%s)' % (repo.url if all else repo.hash)

    for i, lib in enumerate(sorted(repo.libs, key=lambda l: l.name)):
        if prefix:
            nprefix = prefix[:-3] + ('|  ' if prefix[-3] == '|' else '   ')
        else:
            nprefix = ''
        nprefix += '|- ' if i < len(repo.libs)-1 else '`- '

        with cd(lib.path):
            list_(all, nprefix)


@subcommand('status',
    help='Show status of the current %s and its dependencies.' % cwd_type)
def status():
    repo = Repo.fromrepo()
    if repo.scm.dirty():
        action("Status for \"%s\":" % repo.name)
        print repo.scm.status()

    for lib in repo.libs:
        with cd(lib.path):
            status()


@subcommand('compile',
    dict(name=['-t', '--toolchain'], help="Compile toolchain. Example: ARM, uARM, GCC_ARM, IAR"),
    dict(name=['-m', '--mcu'], help="Compile target. Example: K64F, NUCLEO_F401RE, NRF51822..."),
    help='Compile program using the native mbed OS build system.')
def compile(toolchain=None, mcu=None):
    root_path = Repo.findroot(os.getcwd())
    if not root_path:
        Repo.fromrepo()
    with cd(root_path):
        if not os.path.isdir('mbed-os'):
            error('The mbed-os codebase and tools were not found in this program.', -1)

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
            + ['-t', tchain, '-m', target, '--source=.', '--build=%s' % os.path.join('.build', target, tchain)]
            + args,
            env=env)

        
# Export command
@subcommand('export',
    dict(name=['-i', '--ide'], help="IDE to create project files for. Example: UVISION,DS5,IAR", required=True),
    dict(name=['-m', '--mcu'], help="Export for target MCU. Example: K64F, NUCLEO_F401RE, NRF51822..."),
    help='Generate project files for desktop IDEs for the current program.')
def export(ide=None, mcu=None):
    root_path = Repo.findroot(os.getcwd())
    if not root_path:
        Repo.fromrepo()
    with cd(root_path):
        if not os.path.isdir('mbed-os'):
            error('The mbed-os codebase and tools were not found in this program.', -1)

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
            + ['-i', ide, '-m', target, '--source=%s' % repo.path]
            + args,
            env=env)

        
# Build system and exporters
@subcommand('target',
    dict(name='name', nargs='?', help="Default target name. Example: K64F, NUCLEO_F401RE, NRF51822..."),
    help='Set default target for the current program.')
def target(name=None):
    root_path = Repo.findroot(os.getcwd())
    with cd(root_path):
        repo = Repo.fromrepo()
        file = os.path.join(repo.scm.store, 'neo')
        if name is None:
            name = get_cfg(file, 'TARGET')
            action(('The default target for program "%s" is "%s"' % (repo.name, name)) if name else 'No default target is specified for program "%s"' % repo.name)
        else:        
            set_cfg(file, 'TARGET', name)
            action('"%s" now set as default target for program "%s"' % (name, repo.name))

@subcommand('toolchain',
    dict(name='name', nargs='?', help="Default toolchain name. Example: ARM, uARM, GCC_ARM, IAR"),
    help='Sets default toolchain for the current program.')
def toolchain(name=None):
    root_path = Repo.findroot(os.getcwd())
    with cd(root_path):
        repo = Repo.fromrepo()        
        file = os.path.join(repo.scm.store, 'neo')
        if name is None:
            name = get_cfg(file, 'TOOLCHAIN')
            action(('The default toolchain for program "%s" is "%s"' % (repo.name, name)) if name else 'No default toolchain is specified for program "%s"' % repo.name)
        else:
            set_cfg(file, 'TOOLCHAIN', name)
            action('"%s" now set as default toolchain for program "%s"' % (name, repo.name))


# Parse/run command
if len(sys.argv) <= 1:
    parser.print_help()
    sys.exit(1)

args, remainder = parser.parse_known_args()

try:
    log('Working path \"%s\" (%s)' % (os.getcwd(), cwd_type))
    status = args.command(args)
except ProcessException as e:
    error('Subrocess exit with error code %d' % e[0], e[0])
except OSError as e:
    if e[0] == 2:
        error('Could not detect one of the command-line tools.\nPlease verify that you have Git and Mercurial installed and accessible from your current path by executing commands "git" and "hg".\nHint: check the last executed command above.', e[0])
    else:
        error('OS Error: %s' % e[1], e[0])
except KeyboardInterrupt as e:
    error('User aborted!', 255)

sys.exit(status or 0)
