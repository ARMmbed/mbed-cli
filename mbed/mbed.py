#!/usr/bin/env python

# Copyright (c) 2016 ARM Limited, All Rights Reserved
# SPDX-License-Identifier: Apache-2.0

# Licensed under the Apache License, Version 2.0 (the "License"); 
# you may not use this file except in compliance with the License.

# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software 
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, 
# either express or implied.


# pylint: disable=too-many-arguments, too-many-locals, too-many-branches, too-many-lines, line-too-long, too-many-nested-blocks, too-many-public-methods, too-many-instance-attributes
# pylint: disable=invalid-name, missing-docstring

import argparse
import sys
import re
import subprocess
import os
import contextlib
import shutil
import stat
import errno
from itertools import chain, izip, repeat
import urllib
import zipfile


# Default paths to Mercurial and Git
hg_cmd = 'hg'
git_cmd = 'git'
ver = '0.5.2'

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
    ".msub",
    ".meta",
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
    ".mbed",
    "*.settings",
    "mbed_settings.py",

    # Python
    "*.py[cod]",
    "# subrepo ignores",
    ]

# reference to local (unpublished) repo - dir#rev
regex_local_ref = r'^([\w.+-][\w./+-]*?)/?(?:#(.*))?$'

# reference to repo - url#rev
regex_url_ref = r'^(.*/([\w+-]+)(?:\.\w+)?)/?(?:#(.*))?$'

# git url (no #rev)
regex_git_url = r'^(git@|git\://|ssh\://|https?\://)([^/:]+)[:/](.+?)(\.git|\/?)$'

# hg url (no #rev)
regex_hg_url = r'^(file|ssh|https?)://([^/:]+)/([^/]+)/?([^/]+?)?$'

# mbed url is subset of hg. mbed doesn't support ssh transport
regex_mbed_url = r'^(https?)://([\w\-\.]*mbed\.(co\.uk|org|com))/(users|teams)/([\w\-]{1,32})/(repos|code)/([\w\-]+)/?$'
regex_build_url = r'^(https?://([\w\-\.]*mbed\.(co\.uk|org|com))/(users|teams)/([\w\-]{1,32})/(repos|code)/([\w\-]+))/builds/?([\w\-]{12,40}|tip)?/?$'

# default mbed OS url
mbed_os_url = 'https://github.com/ARMmbed/mbed-os'

# default mbed library url
mbed_lib_url = 'https://mbed.org/users/mbed_official/code/mbed/builds/'

# mbed SDK tools needed for programs based on mbed SDK library
mbed_sdk_tools_url = 'https://mbed.org/users/mbed_official/code/mbed-sdk-tools'

# verbose logging
verbose = False
very_verbose = False


# Logging and output
def message(msg):
    return "[mbed] %s\n" % msg

def log(msg, level=1):
    if level <= 0 or verbose:
        sys.stderr.write(message(msg))

def action(msg):
    sys.stderr.write(message(msg))

def warning(msg):
    for line in msg.splitlines():
        sys.stderr.write("[mbed WARNING] %s\n" % line)
    sys.stderr.write("---\n")

def error(msg, code=-1):
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
    log('Exec "'+' '.join(command)+'" in '+os.getcwd())
    try:
        proc = subprocess.Popen(command, **kwargs)
    except OSError as e:
        if e[0] == errno.ENOENT:
            error(
                "Could not execute \"%s\".\n"
                "Please verify that it's installed and accessible from your current path by executing \"%s\".\n" % (command[0], command[0]), e[0])
        else:
            raise e

    if proc.wait() != 0:
        raise ProcessException(proc.returncode, command[0], ' '.join(command), os.getcwd())

def pquery(command, stdin=None, **kwargs):
    if very_verbose:
        log('Query "'+' '.join(command)+'" in '+os.getcwd())
    try:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
    except OSError as e:
        if e[0] == errno.ENOENT:
            error(
                "Could not execute \"%s\".\n"
                "Please verify that it's installed and accessible from your current path by executing \"%s\".\n" % (command[0], command[0]), e[0])
        else:
            raise e

    stdout, _ = proc.communicate(stdin)

    if very_verbose:
        print str(stdout).strip()

    if proc.returncode != 0:
        raise ProcessException(proc.returncode, command[0], ' '.join(command), os.getcwd())

    return stdout

def rmtree_readonly(directory):
    def remove_readonly(func, path, _):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    shutil.rmtree(directory, onerror=remove_readonly)


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

# pylint: disable=no-self-argument, no-method-argument, no-member, no-self-use, unused-argument
@scm('bld')
@staticclass
class Bld(object):
    name = 'bld'

    def isurl(url):
        m_url = re.match(regex_url_ref, url.strip().replace('\\', '/'))
        if m_url:
            return re.match(regex_build_url, m_url.group(1))
        else:
            return False

    def init(path, url):
        if not os.path.exists(path):
            os.mkdir(path)
        with cd(path):
            Bld.seturl(url)

    def clone(url, path=None, depth=None, protocol=None):
        m = Bld.isurl(url)
        if not m:
            raise ProcessException(1, "Not an mbed library build URL")

        try:
            Bld.init(path, url+'/tip')
        except Exception as e:
            error(e[1], e[0])

    def fetch_rev(url, rev):
        tmp_file = '.rev-' + rev + '.zip'
        arch_dir = 'mbed-' + rev
        try:
            if not os.path.exists(tmp_file):
                action("Downloading mbed library build \"%s\" (might take a minute)" % rev)
                urllib.urlretrieve(url, tmp_file)
        except:
            if os.path.isfile(tmp_file):
                os.remove(tmp_file)
            raise Exception(128, "Download failed!\nPlease try again later.")

        try:
            with zipfile.ZipFile(tmp_file) as zf:
                action("Unpacking mbed library build \"%s\" in \"%s\"" % (rev, os.getcwd()))
                zf.extractall()
        except:
            if os.path.isfile(tmp_file):
                os.remove(tmp_file)
            if os.path.isfile(arch_dir):
                rmtree_readonly(arch_dir)
            raise Exception(128, "An error occurred while unpacking mbed library archive \"%s\" in \"%s\"" % (tmp_file, os.getcwd()))

    def checkout(rev):
        url = Bld.geturl()
        m = Bld.isurl(url)
        if not m:
            raise ProcessException(1, "Not an mbed library build URL")
        rev = Hg.remoteid(m.group(1), rev)
        if not rev:
            error("Unable to fetch late mbed library revision")

        if rev != Bld.getrev():
            log("Cleaning up library build folder")
            for fl in os.listdir('.'):
                if not fl.startswith('.'):
                    if os.path.isfile(fl):
                        os.remove(fl)
                    else:
                        shutil.rmtree(fl)

            log("Checkout \"%s\" in %s" % (rev, os.path.basename(os.getcwd())))
            arch_url = m.group(1) + '/archive/' + rev + '.zip'
            arch_dir = m.group(7) + '-' + rev
            try:
                if not os.path.exists(arch_dir):
                    Bld.fetch_rev(arch_url, rev)
            except Exception as e:
                if os.path.exists(arch_dir):
                    rmtree_readonly(arch_dir)
                error(e[1], e[0])
            Bld.seturl(url+'/'+rev)

    def update(rev=None, clean=False, is_local=False):
        return Bld.checkout(rev)

    def untracked():
        return ""

    def seturl(url):
        if not os.path.exists('.'+Bld.name):
            os.mkdir('.'+Bld.name)

        fl = os.path.join('.'+Bld.name, 'bldrc')
        try:
            with open(fl, 'w') as f:
                f.write(url)
        except IOError:
            error("Unable to write bldrc file in \"%s\"" % fl, 1)

    def geturl():
        with open(os.path.join('.bld', 'bldrc')) as f:
            url = f.read().strip()
        m = Bld.isurl(url)
        return m.group(1)+'/builds' if m else ''

    def getrev():
        with open(os.path.join('.bld', 'bldrc')) as f:
            url = f.read().strip()
        m = Bld.isurl(url)
        return m.group(8) if m else ''

    def getbranch():
        return "default"


# pylint: disable=no-self-argument, no-method-argument, no-member, no-self-use, unused-argument
@scm('hg')
@staticclass
class Hg(object):
    name = 'hg'
    ignore_file = os.path.join('.hg', 'hgignore')

    def isurl(url):
        m_url = re.match(regex_url_ref, url.strip().replace('\\', '/'))
        if m_url:
            return ((re.match(regex_hg_url, m_url.group(1)) or re.match(regex_mbed_url, m_url.group(1)))
                and not re.match(regex_build_url, m_url.group(1)))
        else:
            return False

    def init(path=None):
        popen([hg_cmd, 'init'] + ([path] if path else []) + (['-v'] if verbose else ['-q']))

    def clone(url, name=None, depth=None, protocol=None):
        popen([hg_cmd, 'clone', formaturl(url, protocol), name] + (['-v'] if verbose else ['-q']))

    def add(dest):
        log("Adding reference \"%s\"" % dest)
        try:
            popen([hg_cmd, 'add', dest] + (['-v'] if verbose else ['-q']))
        except ProcessException:
            pass

    def remove(dest):
        log("Removing reference \"%s\" " % dest)
        try:
            popen([hg_cmd, 'rm', '-f', dest] + (['-v'] if verbose else ['-q']))
        except ProcessException:
            pass

    def commit():
        popen([hg_cmd, 'commit'] + (['-v'] if verbose else ['-q']))

    def publish(all=None):
        popen([hg_cmd, 'push'] + (['--new-branch'] if all else []) + (['-v'] if verbose else ['-q']))

    def fetch():
        log("Fetching revisions from remote repository to \"%s\"" % os.path.basename(os.getcwd()))
        popen([hg_cmd, 'pull'] + (['-v'] if verbose else ['-q']))

    def discard():
        log("Discarding local changes in \"%s\"" % os.path.basename(os.getcwd()))
        popen([hg_cmd, 'update', '-C'] + (['-v'] if verbose else ['-q']))

    def checkout(rev):
        log("Checkout \"%s\" in %s to %s" % (rev, os.path.basename(os.getcwd()), rev))
        popen([hg_cmd, 'update'] + (['-r', rev] if rev else []) + (['-v'] if verbose else ['-q']))

    def update(rev=None, clean=False, is_local=False):
        if clean:
            Hg.discard()
        if not is_local:
            Hg.fetch()
        Hg.checkout(rev)

    def status():
        return pquery([hg_cmd, 'status'] + (['-v'] if verbose else ['-q']))

    def dirty():
        return pquery([hg_cmd, 'status', '-q'])

    def untracked():
        result = pquery([hg_cmd, 'status', '-u'])
        return re.sub(r'^\? ', '', result).splitlines()

    def outgoing():
        try:
            pquery([hg_cmd, 'outgoing'])
            return 1
        except ProcessException as e:
            if e[0] != 1:
                raise e
            return 0

    def geturl():
        tagpaths = '[paths]'
        default_url = ''
        url = ''
        if os.path.isfile(os.path.join('.hg', 'hgrc')):
            with open(os.path.join('.hg', 'hgrc')) as f:
                lines = f.read().splitlines()
                if tagpaths in lines:
                    idx = lines.index(tagpaths)
                    m = re.match(r'^([\w_]+)\s*=\s*(.*)?$', lines[idx+1])
                    if m:
                        if m.group(1) == 'default':
                            default_url = m.group(2)
                        else:
                            url = m.group(2)
            if default_url:
                url = default_url

        return formaturl(url or pquery([hg_cmd, 'paths', 'default']).strip())

    def getrev():
        if os.path.isfile(os.path.join('.hg', 'dirstate')):
            with open(os.path.join('.hg', 'dirstate'), 'rb') as f:
                return ''.join('%02x'%ord(i) for i in f.read(6))
        else:
            return ""

    def getbranch():
        return pquery([hg_cmd, 'branch']).strip() or ""

    def remoteid(url, rev=None):
        return pquery([hg_cmd, 'id', '--id', url] + (['-r', rev] if rev else [])).strip() or ""

    def hgrc():
        hook = 'ignore.local = .hg/hgignore'
        hgrc = os.path.join('.hg', 'hgrc')
        try:
            with open(hgrc) as f:
                exists = hook in f.read().splitlines()
        except IOError:
            exists = False

        if not exists:
            try:
                with open(hgrc, 'a') as f:
                    f.write('[ui]\n')
                    f.write(hook + '\n')
            except IOError:
                error("Unable to write hgrc file in \"%s\"" % hgrc, 1)

    def ignores():
        Hg.hgrc()
        try:
            with open(Hg.ignore_file, 'w') as f:
                f.write("syntax: glob\n"+'\n'.join(ignores)+'\n')
        except IOError:
            error("Unable to write ignore file in \"%s\"" % os.path.join(os.getcwd(), Hg.ignore_file), 1)

    def ignore(dest):
        Hg.hgrc()
        try:
            with open(Hg.ignore_file) as f:
                exists = dest in f.read().splitlines()
        except IOError:
            exists = False

        if not exists:
            try:
                with open(Hg.ignore_file, 'a') as f:
                    f.write(dest + '\n')
            except IOError:
                error("Unable to write ignore file in \"%s\"" % os.path.join(os.getcwd(), Hg.ignore_file), 1)

    def unignore(dest):
        Hg.ignore_file = os.path.join('.hg', 'hgignore')
        try:
            with open(Hg.ignore_file) as f:
                lines = f.read().splitlines()
        except IOError:
            lines = []

        if dest in lines:
            lines.remove(dest)
            try:
                with open(Hg.ignore_file, 'w') as f:
                    f.write('\n'.join(lines) + '\n')
            except IOError:
                error("Unable to write ignore file in \"%s\"" % os.path.join(os.getcwd(), Hg.ignore_file), 1)

# pylint: disable=no-self-argument, no-method-argument, no-member, no-self-use, unused-argument
@scm('git')
@staticclass
class Git(object):
    name = 'git'
    ignore_file = os.path.join('.git', 'info', 'exclude')

    def isurl(url):
        m_url = re.match(regex_url_ref, url.strip().replace('\\', '/'))
        if m_url:
            return (re.match(regex_git_url, m_url.group(1))
                and not re.match(regex_mbed_url, m_url.group(1))
                and not re.match(regex_build_url, m_url.group(1)))
        else:
            return False

    def init(path=None):
        popen([git_cmd, 'init'] + ([path] if path else []) + ([] if verbose else ['-q']))

    def clone(url, name=None, depth=None, protocol=None):
        popen([git_cmd, 'clone', formaturl(url, protocol), name] + (['--depth', depth] if depth else []) + (['-v'] if verbose else ['-q']))

    def add(dest):
        log("Adding reference "+dest)
        try:
            popen([git_cmd, 'add', dest] + (['-v'] if verbose else []))
        except ProcessException:
            pass

    def remove(dest):
        log("Removing reference "+dest)
        try:
            popen([git_cmd, 'rm', '-f', dest] + ([] if verbose else ['-q']))
        except ProcessException:
            pass

    def commit():
        popen([git_cmd, 'commit', '-a'] + (['-v'] if verbose else ['-q']))

    def publish(all=None):
        if all:
            popen([git_cmd, 'push', '--all'] + (['-v'] if verbose else ['-q']))
        else:
            remote = Git.getremote()
            branch = Git.getbranch()
            if remote and branch:
                popen([git_cmd, 'push', remote, branch] + (['-v'] if verbose else ['-q']))
            else:
                err = "Unable to publish outgoing changes for \"%s\" in \"%s\".\n" % (os.path.basename(os.getcwd()), os.getcwd())
                if not remote:
                    error(err+"The local repository is not associated with a remote one.", 1)
                if not branch:
                    error(err+"Working set is not on a branch.", 1)

    def fetch():
        log("Fetching revisions from remote repository to \"%s\"" % os.path.basename(os.getcwd()))
        popen([git_cmd, 'fetch', '--all'] + (['-v'] if verbose else ['-q']))

    def discard():
        log("Discarding local changes in \"%s\"" % os.path.basename(os.getcwd()))
        popen([git_cmd, 'reset', 'HEAD'] + ([] if verbose else ['-q'])) # unmarks files for commit
        popen([git_cmd, 'checkout', '.'] + ([] if verbose else ['-q'])) # undo  modified files
        popen([git_cmd, 'clean', '-fdq'] + ([] if verbose else ['-q'])) # cleans up untracked files and folders

    def merge(dest):
        log("Merging \"%s\" with \"%s\"" % (os.path.basename(os.getcwd()), dest))
        popen([git_cmd, 'merge', dest] + (['-v'] if verbose else ['-q']))

    def checkout(rev):
        if not rev:
            return
        log("Checkout \"%s\" in %s to %s" % (rev, os.path.basename(os.getcwd()), rev))
        popen([git_cmd, 'checkout', rev] + ([] if verbose else ['-q']))
        if Git.isdetached(): # try to find associated refs to avoid detached state
            refs = Git.getrefs(rev)
            for ref in refs: # re-associate with a local or remote branch (rev is the same)
                branch = re.sub(r'^(.*?)\/(.*?)$', r'\2', ref)
                log("Revision \"%s\" matches a branch \"%s\"reference. Re-associating with branch" % (rev, branch))
                popen([git_cmd, 'checkout', branch] + ([] if verbose else ['-q']))
                break

    def update(rev=None, clean=False, is_local=False):
        if clean:
            Git.discard()
        if not is_local:
            Git.fetch()
        if rev:
            Git.checkout(rev)
        else:
            remote = Git.getremote()
            branch = Git.getbranch()
            if remote and branch:
                Git.merge('%s/%s' % (remote, branch))
            else:
                err = "Unable to update \"%s\" in \"%s\".\n" % (os.path.basename(os.getcwd()), os.getcwd())
                if not remote:
                    log(err+"The local repository is not associated with a remote one.")
                if not branch:
                    log(err+"Working set is not on a branch.")

    def status():
        return pquery([git_cmd, 'status', '-s'] + (['-v'] if verbose else []))

    def dirty():
        return pquery([git_cmd, 'status', '-uno', '--porcelain'])

    def untracked():
        return pquery([git_cmd, 'ls-files', '--others', '--exclude-standard']).splitlines()

    def outgoing():
        # Get default remote
        remote = Git.getremote()
        if not remote:
            return -1

        # Get current branch
        branch = Git.getbranch()
        if not branch:
            # Detached mode is okay as we don't expect the user to publish from detached state without branch
            return 0

        try:
            # Check if remote branch exists
            if not pquery([git_cmd, 'rev-parse', '%s/%s' % (remote, branch)]):
                return 1
        except ProcessException:
            return 1

        # Check for outgoing commits for the same remote branch
        return 1 if pquery([git_cmd, 'log', '%s/%s..%s' % (remote, branch, branch)]) else 0

    # Checks whether current working tree is detached
    def isdetached():
        return True if Git.getbranch() == "" else False

    # Finds default remote
    def getremote():
        remote = None
        remotes = Git.getremotes('push')
        for r in remotes:
            remote = r[0]
            # Prefer origin which is Git's default remote when cloning
            if r[0] == "origin":
                break
        return remote

    # Finds all associated remotes for the specified remote type
    def getremotes(rtype='fetch'):
        result = []
        remotes = pquery([git_cmd, 'remote', '-v']).strip().splitlines()
        for remote in remotes:
            remote = re.split(r'\s', remote)
            t = re.sub('[()]', '', remote[2])
            if not rtype or rtype == t:
                result.append([remote[0], remote[1], t])
        return result

    def geturl():
        url = ""
        remotes = Git.getremotes()
        for remote in remotes:
            url = remote[1]
            if remote[0] == "origin": # Prefer origin URL
                break
        return formaturl(url)

    def getrev():
        return pquery([git_cmd, 'rev-parse', 'HEAD']).strip()

    # Gets current branch or returns empty string if detached
    def getbranch():
        branch = pquery([git_cmd, 'rev-parse', '--symbolic-full-name', '--abbrev-ref', 'HEAD']).strip()
        return branch if branch != "HEAD" else ""

    # Finds refs (local or remote branches). Will match rev if specified
    def getrefs(rev=None, ret_rev=False):
        result = []
        lines = pquery([git_cmd, 'show-ref']).strip().splitlines()
        for line in lines:
            m = re.match(r'^(.+)\s+(.+)$', line)
            if m and (not rev or m.group(1).startswith(rev)):
                if re.match(r'refs\/(heads|remotes)\/', m.group(2)): # exclude tags
                    result.append(m.group(1) if ret_rev else re.sub(r'refs\/(heads|remotes)\/', '', m.group(2)))
        return result

    # Finds branches a rev belongs to
    def revbranches(rev):
        branches = []
        lines = pquery([git_cmd, 'branch', '-a', '--contains'] + ([rev] if rev else [])).strip().splitlines()
        for line in lines:
            if re.match(r'^\*?\s+\((.+)\)$', line):
                continue
            line = re.sub(r'\s+', '', line)
            branches.append(line)
        return branches

    def ignores():
        try:
            with open(Git.ignore_file, 'w') as f:
                f.write('\n'.join(ignores)+'\n')
        except IOError:
            error("Unable to write ignore file in \"%s\"" % os.path.join(os.getcwd(), Git.ignore_file), 1)

    def ignore(dest):
        try:
            with open(Git.ignore_file) as f:
                exists = dest in f.read().splitlines()
        except IOError:
            exists = False

        if not exists:
            try:
                with open(Git.ignore_file, 'a') as f:
                    f.write(dest.replace("\\", "/") + '\n')
            except IOError:
                error("Unable to write ignore file in \"%s\"" % os.path.join(os.getcwd(), Git.ignore_file), 1)
    def unignore(dest):
        try:
            with open(Git.ignore_file) as f:
                lines = f.read().splitlines()
        except IOError:
            lines = []

        if dest in lines:
            lines.remove(dest)
            try:
                with open(Git.ignore_file, 'w') as f:
                    f.write('\n'.join(lines) + '\n')
            except IOError:
                error("Unable to write ignore file in \"%s\"" % os.path.join(os.getcwd(), Git.ignore_file), 1)

# Repository object
class Repo(object):
    is_local = False
    is_build = False
    name = None
    path = None
    url = None
    rev = None
    scm = None
    libs = []

    @classmethod
    def fromurl(cls, url, path=None):
        repo = cls()
        m_local = re.match(regex_local_ref, url.strip().replace('\\', '/'))
        m_repo_url = re.match(regex_url_ref, url.strip().replace('\\', '/'))
        m_bld_url = re.match(regex_build_url, url.strip().replace('\\', '/'))
        if m_local:
            repo.name = os.path.basename(path or m_local.group(1))
            repo.path = os.path.abspath(path or os.path.join(os.getcwd(), m_local.group(1)))
            repo.url = m_local.group(1)
            repo.rev = m_local.group(2)
            repo.is_local = True
        elif m_bld_url:
            repo.name = os.path.basename(path or m_bld_url.group(7))
            repo.path = os.path.abspath(path or os.path.join(os.getcwd(), repo.name))
            repo.url = m_bld_url.group(1)+'/builds'
            repo.rev = m_bld_url.group(8)
            repo.is_build = True
        elif m_repo_url:
            repo.name = os.path.basename(path or m_repo_url.group(2))
            repo.path = os.path.abspath(path or os.path.join(os.getcwd(), repo.name))
            repo.url = formaturl(m_repo_url.group(1))
            repo.rev = m_repo_url.group(3)
        else:
            error('Invalid repository (%s)' % url.strip(), -1)
        return repo

    @classmethod
    def fromlib(cls, lib=None):
        with open(lib) as f:
            ref = f.read(200)
            if ref.startswith('!<arch>'):
                warning(
                    "A static library \"%s\" in \"%s\" uses a non-standard .lib file extension, which is not compatible with the mbed build tools.\n"
                    "Please change the extension of \"%s\" (for example to \"%s\").\n" % (os.path.basename(lib), os.path.split(lib)[0], os.path.basename(lib), os.path.basename(lib).replace('.lib', '.ar')))
                return False
            else:
                return cls.fromurl(ref, lib[:-4])

    @classmethod
    def fromrepo(cls, path=None):
        repo = cls()
        if path is None:
            path = Repo.findparent(os.getcwd())
            if path is None:
                error(
                    "Could not find mbed program in current path \"%s\".\n"
                    "You can fix this by calling \"mbed new .\" or \"mbed default root .\" in the root of your program." % os.getcwd())

        repo.path = os.path.abspath(path)
        repo.name = os.path.basename(repo.path)

        repo.sync()

        if repo.scm is None:
            warning(
                "Program \"%s\" in \"%s\" does not use source control management.\n"
                "To fix this you should use \"mbed new .\" in the root of your program." % (repo.name, repo.path))

        return repo

    @classmethod
    def isrepo(cls, path=None):
        for name, _ in scms.items():
            if os.path.isdir(os.path.join(path, '.'+name)):
                return True

        return False

    @classmethod
    def findparent(cls, path=None):
        path = os.path.abspath(path or os.getcwd())

        while cd(path):
            if os.path.isfile(os.path.join(path, Program.config_file)) or Repo.isrepo(path):
                return path

            tpath = path
            path = os.path.split(path)[0]
            if tpath == path:
                break

        return None

    @classmethod
    def pathtype(cls, path=None):
        path = os.path.abspath(path or os.getcwd())

        depth = 0
        while cd(path):
            tpath = path
            path = Repo.findparent(path)
            if path:
                depth += 1
                path = os.path.split(path)[0]
                if tpath == path:       # Reached root.
                    break
            else:
                break

        return "directory" if depth == 0 else ("program" if depth == 1 else "library")

    @classmethod
    def revtype(cls, rev, ret_rev=False):
        if rev is None or len(rev) == 0:
            return 'latest' + (' revision in the current branch' if ret_rev else '')
        elif re.match(r'^([a-zA-Z0-9]{12,40})$', rev) or re.match(r'^([0-9]+)$', rev):
            return 'rev' + (' #'+rev if ret_rev else '')
        else:
            return 'branch' + (' '+rev if ret_rev else '')

    @property
    def lib(self):
        return self.path + '.' + ('bld' if self.is_build else 'lib')

    @property
    def fullurl(self):
        if self.url:
            return (self.url.rstrip('/') + '/' +
                    (('' if self.is_build else '#') +
                        self.rev if self.rev else ''))

    def sync(self):
        self.url = None
        self.rev = None
        if os.path.isdir(self.path):
            try:
                self.scm = self.getscm()
                if self.scm and self.scm.name == 'bld':
                    self.is_build = True
            except ProcessException:
                pass

            try:
                self.url = self.geturl()
                if not self.url:
                    self.is_local = True
                    ppath = self.findparent(os.path.split(self.path)[0])
                    self.url = relpath(ppath, self.path).replace("\\", "/") if ppath else os.path.basename(self.path)
            except ProcessException:
                pass

            try:
                self.rev = self.getrev()
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

    # Pass backend SCM commands and parameters if SCM exists
    def __wrap_scm(self, method):
        def __scm_call(*args, **kwargs):
            if self.scm and hasattr(self.scm, method) and callable(getattr(self.scm, method)):
                with cd(self.path):
                    return getattr(self.scm, method)(*args, **kwargs)    
        return __scm_call

    def __getattr__(self, attr):      
        if attr in ['geturl', 'getrev', 'add',  'remove', 'ignores', 'ignore', 'unignore',
                    'status', 'dirty', 'commit', 'outgoing', 'publish', 'checkout', 'update',
                    'isdetached']:
            wrapper = self.__wrap_scm(attr)
            self.__dict__[attr] = wrapper
            return wrapper
        else:
            raise AttributeError("Repo instance doesn't have attribute '%s'" % attr)

    def remove(self, dest, *args, **kwargs):
        if os.path.isfile(dest):
            try:
                os.remove(dest)
            except OSError:
                pass
        return self.scm.remove(dest, *args, **kwargs)

    def getlibs(self):
        for root, dirs, files in os.walk(self.path):
            dirs[:] = [d for d in dirs  if not d.startswith('.')]
            files[:] = [f for f in files if not f.startswith('.')]

            for f in files:
                if f.endswith('.lib') or f.endswith('.bld'):
                    repo = Repo.fromlib(os.path.join(root, f))
                    if repo:
                        yield repo
                    if f[:-4] in dirs:
                        dirs.remove(f[:-4])

    def write(self):
        if os.path.isfile(self.lib):
            with open(self.lib) as f:
                lib_repo = Repo.fromurl(f.read().strip())
                if (formaturl(lib_repo.url, 'https') == formaturl(self.url, 'https') # match URLs in common format (https)
                        and (lib_repo.rev == self.rev                              # match revs, even if rev is None (valid for repos with no revisions)
                             or (lib_repo.rev and self.rev
                                 and lib_repo.rev == self.rev[0:len(lib_repo.rev)]))):  # match long and short rev formats
                    #print self.name, 'unmodified'
                    return

        action("Updating reference \"%s\" -> \"%s\"" % (relpath(cwd_root, self.path) if cwd_root != self.path else self.name, self.fullurl))

        with open(self.lib, 'wb') as f:
            f.write(self.fullurl + '\n')

    def rm_untracked(self):
        untracked = self.scm.untracked()
        for f in untracked:
            if re.match(r'(.+)\.(lib|bld)$', f) and os.path.isfile(f):
                action("Remove untracked library reference \"%s\"" % f)
                os.remove(f)

    def can_update(self, clean, force):
        err = None
        if (self.is_local or self.url is None) and not force:
            err = (
                "Preserving local library \"%s\" in \"%s\".\nPlease publish this library to a remote URL to be able to restore it at any time."
                "You can use --ignore switch to ignore all local libraries and update only the published ones.\n"
                "You can also use --force switch to remove all local libraries. WARNING: This action cannot be undone." % (self.name, self.path))
        elif not clean and self.dirty():
            err = (
                "Uncommitted changes in \"%s\" in \"%s\".\nPlease discard or stash them first and then retry update.\n"
                "You can also use --clean switch to discard all uncommitted changes. WARNING: This action cannot be undone." % (self.name, self.path))
        elif not force and self.outgoing():
            err = (
                "Unpublished changes in \"%s\" in \"%s\".\nPlease publish them first using the \"publish\" command.\n"
                "You can also use --force to discard all local commits and replace the library with the one included in this revision. WARNING: This action cannot be undone." % (self.name, self.path))

        return (False, err) if err else (True, "OK")

    def check_repo(self, show_warning=None):
        err = None
        if not os.path.isdir(self.path):
            err = (
                "Library reference \"%s\" points to non-existing library in \"%s\"\n"
                "You can use \"mbed deploy\" to import the missing libraries.\n"
                "You can also use \"mbed sync\" to synchronize and remove all invalid library references." % (os.path.basename(self.lib), self.path))
        elif not self.isrepo(self.path):
            err = (
                "Library reference \"%s\" points to a folder \"%s\", which is not a valid repository.\n"
                "You can remove the conflicting folder manually and use \"mbed deploy\" to import the missing libraries\n"
                "You can also remove library reference \"%s\" and use \"mbed sync\" again." % (os.path.basename(self.lib), self.path, self.lib))

        if err:
            if show_warning:
                warning(err)
            else:
                error(err, 1)
            return False
        return True


# Program object, used to indicate the root of the code base
class Program(object):
    config_file = ".mbed"
    path = None
    name = None
    is_cwd = False
    is_repo = False

    def __init__(self, path=None, print_warning=False):
        path = os.path.abspath(path or os.getcwd())
        self.path = path
        self.is_cwd = True

        while cd(path):
            tpath = path
            if os.path.isfile(os.path.join(path, Program.config_file)):
                self.path = path
                self.is_cwd = False
                break

            path = os.path.split(path)[0]
            if tpath == path:       # Reached root.
                break

        self.name = os.path.basename(self.path)

        # is_cwd flag indicates that current dir is assumed to be root, not root repo
        if self.is_cwd and print_warning:
            warning(
                "Could not find mbed program in current path \"%s\".\n"
                "You can fix this by calling \"mbed new .\" or \"mbed default root .\" in the root of your program." % self.path)
 
    # Sets config value
    def set_cfg(self, var, val):
        fl = os.path.join(self.path, self.config_file)
        try:
            with open(fl) as f:
                lines = f.read().splitlines()
        except IOError:
            lines = []

        for line in lines:
            m = re.match(r'^([\w+-]+)\=(.*)?$', line)
            if m and m.group(1) == var:
                lines.remove(line)

        lines += [var+"="+val]

        with open(fl, 'w') as f:
            f.write('\n'.join(lines) + '\n')

    # Gets config value
    def get_cfg(self, var, default_val=None):
        fl = os.path.join(self.path, self.config_file)
        try:
            with open(fl) as f:
                lines = f.read().splitlines()
        except IOError:
            lines = []

        for line in lines:
            m = re.match(r'^([\w+-]+)\=(.*)?$', line)
            if m and m.group(1) == var:
                return m.group(2)
        return default_val

    def set_root(self):
        return self.set_cfg('ROOT', '.')

    def unset_root(self, path=None):
        fl = os.path.join(path or self.path, self.config_file)
        if os.path.isfile(fl):
            os.remove(fl)

    # Gets mbed OS dir (unified)
    def get_os_dir(self):
        if os.path.isdir(os.path.join(self.path, 'mbed-os')):
            return os.path.join(self.path, 'mbed-os')
        elif self.name == 'mbed-os':
            return self.path
        else:
            return None

    def get_mbedlib_dir(self):
        if os.path.isdir(os.path.join(self.path, 'mbed')):
            return os.path.join(self.path, 'mbed')
        else:
            return None

    # Gets mbed tools dir (unified)
    def get_tools_dir(self):
        mbed_os_path = self.get_os_dir()
        # mbed-os dir identified and tools is a sub dir
        if mbed_os_path and os.path.isdir(os.path.join(mbed_os_path, 'tools')):
            return os.path.join(mbed_os_path, 'tools')
        # mbed-os not identified but tools found under cwd/tools
        elif os.path.isdir(os.path.join(self.path, 'tools')):
            return os.path.join(self.path, 'tools')
        # mbed Classic deployed tools
        elif os.path.isdir(os.path.join(self.path, '.temp', 'tools')):
            return os.path.join(self.path, '.temp', 'tools')
        else:
            return None

    # Routines after cloning mbed-os
    def post_action(self):
        mbed_tools_path = self.get_tools_dir()

        if not mbed_tools_path:
            if not os.path.exists(os.path.join(self.path, '.temp')):
                os.mkdir(os.path.join(self.path, '.temp'))
            self.add_tools(os.path.join(self.path, '.temp'))
            mbed_tools_path = self.get_tools_dir()

        if not mbed_tools_path:
            warning("Cannot find the mbed tools directory in \"%s\"" % self.path)
            return False

        if (not os.path.isfile(os.path.join(self.path, 'mbed_settings.py')) and
                os.path.isfile(os.path.join(mbed_tools_path, 'default_settings.py'))):
            shutil.copy(os.path.join(mbed_tools_path, 'default_settings.py'), os.path.join(self.path, 'mbed_settings.py'))

        mbed_os_path = self.get_os_dir()
        if not mbed_os_path:
            return False

        missing = []
        fname = 'requirements.txt'
        try:
            import pip
            installed_packages = [package.project_name.lower() for package in pip.get_installed_distributions()]
            with open(os.path.join(mbed_os_path, fname), 'r') as f:
                for line in f.read().splitlines():
                    pkg = re.sub(r'^([\w-]+).*$', r'\1', line).lower()
                    if not pkg in installed_packages:
                        missing.append(pkg)
        except IOError:
            pass
        except ImportError:
            pass

        if len(missing):
            warning(
                "-------------------------------------------------------------------------------\n"
                "The mbed build tools in this program require Python modules that are not installed.\n"
                "This might prevent you from compiling your code or exporting to IDEs and other toolchains.\n"
                "The missing Python modules are: %s\n"
                "You can install all missing modules by opening a command prompt in \"%s\" and running \"pip install -r %s\"" % (', '.join(missing), mbed_os_path, fname))

    def add_tools(self, path):
        with cd(path):
            tools_dir = 'tools'
            if not os.path.exists(tools_dir):
                try:
                    action("Couldn't find build tools in your program. Downloading the mbed SDK tools...")
                    Hg.clone(mbed_sdk_tools_url, tools_dir)
                except:
                    if os.path.exists(tools_dir):
                        rmtree_readonly(tools_dir)
                    raise Exception(128, "An error occurred while cloning the mbed SDK tools from \"%s\"" % mbed_sdk_tools_url)

    def get_tools(self):
        mbed_tools_path = self.get_tools_dir()
        if not mbed_tools_path:
            error('The mbed tools were not found in "%s". \n Run `mbed deploy` to install dependencies and tools. ' % self.path, -1)
        return mbed_tools_path

    def get_mcu(self, mcu=None):
        target = mcu if mcu else self.get_cfg('TARGET')
        if target is None:
            error('Please specify compile target using the -m switch or set default target using command "target"', 1)
        return target

    def get_toolchain(self, toolchain=None):
        tchain = toolchain if toolchain else self.get_cfg('TOOLCHAIN')
        if tchain is None:
            error('Please specify compile toolchain using the -t switch or set default toolchain using command "toolchain"', 1)
        return tchain

    def get_macros(self):
        macros = []
        if os.path.isfile('MACROS.txt'):
            with open('MACROS.txt') as f:
                macros = f.read().splitlines()
        return macros


def formaturl(url, format="default"):
    url = "%s" % url
    m = re.match(regex_mbed_url, url)
    if m:
        if format == "http":
            url = 'http://%s/%s/%s/%s/%s' % (m.group(2), m.group(4), m.group(5), m.group(6), m.group(7))
        else:
            url = 'https://%s/%s/%s/%s/%s' % (m.group(2), m.group(4), m.group(5), m.group(6), m.group(7))
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
cwd_root = os.getcwd()
cwd_type = Repo.pathtype(cwd_root)
cwd_dest = "program" if cwd_type == "directory" else "library"

# Subparser handling
parser = argparse.ArgumentParser(description="Command-line code management tool for ARM mbed OS - http://www.mbed.com\nversion %s" % ver)
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

        subparser.add_argument("-v", "--verbose", action="store_true", dest="verbose", help="Verbose diagnostic output")
        subparser.add_argument("-vv", "--very_verbose", action="store_true", dest="very_verbose", help="Very verbose diagnostic output")

        def thunk(parsed_args):
            argv = [arg['dest'] if 'dest' in arg else arg['name'] for arg in args]
            argv = [(arg if isinstance(arg, basestring) else arg[-1]).strip('-').replace('-', '_')
                    for arg in argv]
            argv = {arg: vars(parsed_args)[arg] for arg in argv
                    if vars(parsed_args)[arg] is not None}

            return command(**argv)

        subparser.set_defaults(command=thunk)
        return command
    return subcommand


# New command
@subcommand('new',
    dict(name='name', help='Destination name or path'),
    dict(name='--scm', nargs='?', help='Source control management. Currently supported: %s. Default: git' % ', '.join([s.name for s in scms.values()])),
    dict(name='--program', action='store_true', help='Force creation of an mbed program. Default: auto.'),
    dict(name='--library', action='store_true', help='Force creation of an mbed library. Default: auto.'),
    dict(name='--mbedlib', action='store_true', help='Add the mbed library instead of mbed-os into the program.'),
    dict(name='--create-only', action='store_true', help='Only create program, do not import mbed-os or mbed library.'),
    dict(name='--depth', nargs='?', help='Number of revisions to fetch the mbed OS repository when creating new program. Default: all revisions.'),
    dict(name='--protocol', nargs='?', help='Transport protocol when fetching the mbed OS repository when creating new program. Supported: https, http, ssh, git. Default: inferred from URL.'),
    help='Create a new program based on the specified source control management. Will create a new library when called from inside a program. Supported SCMs: %s.' % (', '.join([s.name for s in scms.values()])))
def new(name, scm='git', program=False, library=False, mbedlib=False, create_only=False, depth=None, protocol=None):
    global cwd_root

    d_path = name or os.getcwd()
    p_path = Repo.findparent(d_path) or d_path
    if program and library:
        error("Cannot use both --program and --library options.", 1)
    elif not program and not library:
        d_type = 'library' if os.path.abspath(p_path) != os.path.abspath(d_path) else 'program'
    else:
        d_type = 'library' if library else 'program'

    if scm and scm != 'none':
        if os.path.isdir(d_path) and Repo.isrepo(d_path):
            repo = Repo.fromrepo(d_path)
            if repo.scm.name != scm:
                error("A repository already exists in \"%s\" based on %s. Please select a different name or location." % (d_path, scm), 1)
        else:
            repo_scm = [s for s in scms.values() if s.name == scm.lower()]
            if not repo_scm:
                error(
                    "You have specified invalid source control management system\n"
                    "Please specify one of the following SCMs: %s" % ', '.join([s.name for s in scms.values()]), 1)
            repo_scm[0].init(d_path)
    else:
        scm = 'folder'
        if not os.path.isdir(d_path):
            os.mkdir(d_path)

    if len(os.listdir(d_path)) > 1:
        warning("Directory \"%s\" is not empty." % d_path)

    action("Creating new %s \"%s\" (%s)" % (d_type, os.path.basename(d_path), scm))
    p = Program(d_path)

    if d_type == 'program':
        # This helps sub-commands to display relative paths to the created program
        cwd_root = os.path.abspath(d_path)
        p.path = cwd_root
        p.set_root()
        if not create_only and not p.get_os_dir() and not p.get_mbedlib_dir():
            url = mbed_lib_url if mbedlib else mbed_os_url
            try:
                with cd(d_path):
                    add(url, depth=depth, protocol=protocol, top=False)
            except Exception as e:
                d = 'mbed' if mbedlib else 'mbed-os'
                if os.path.isdir(os.path.join(d_path, d)):
                    rmtree_readonly(os.path.join(d_path, d))
                raise e
        if d_path:
            os.chdir(d_path)
    else:
        p.unset_root(d_path)
        with cd(p_path):
            sync()

    Program(d_path).post_action()


# Import command
@subcommand('import',
    dict(name='url', help='URL of the %s' % cwd_dest),
    dict(name='path', nargs='?', help='Destination name or path. Default: current %s.' % cwd_type),
    dict(name=['-I', '--ignore'], action='store_true', help='Ignore errors related to cloning and updating.'),
    dict(name='--depth', nargs='?', help='Number of revisions to fetch from the remote repository. Default: all revisions.'),
    dict(name='--protocol', nargs='?', help='Transport protocol for the source control management. Supported: https, http, ssh, git. Default: inferred from URL.'),
    help='Import a program and its dependencies into the current directory or specified destination path.')
def import_(url, path=None, ignore=False, depth=None, protocol=None, top=True):
    global cwd_root

    repo = Repo.fromurl(url, path)
    if top:
        if cwd_type != "directory":
            error("Cannot import program in the specified location \"%s\" because it's already part of a program.\n"
                  "Please change your working directory to a different location or use \"mbed add\" to import the URL as a library." % os.path.abspath(repo.path), 1)
    else:
        program = Program()
        protocol = program.get_cfg('PROTOCOL', protocol)

    if os.path.isdir(repo.path) and len(os.listdir(repo.path)) > 1:
        error("Directory \"%s\" is not empty. Please ensure that the destination folder is empty." % repo.path, 1)

    # Sorted so repositories that match urls are attempted first
    sorted_scms = [(scm.isurl(url), scm) for scm in scms.values()]
    sorted_scms = sorted(sorted_scms, key=lambda (m, _): not m)

    text = "Importing program" if top else "Adding library"
    action("%s \"%s\" from \"%s/\"%s" % (text, relpath(cwd_root, repo.path), repo.url, ' at '+(repo.revtype(repo.rev, True))))
    for _, scm in sorted_scms:
        try:
            scm.clone(repo.url, repo.path, depth=depth, protocol=protocol)
            repo.scm = scm
            repo.ignores()

            with cd(repo.path):
                Program(repo.path).set_root()
                try:
                    repo.checkout(repo.rev)
                except ProcessException as e:
                    err = "Unable to update \"%s\" to %s" % (repo.name, repo.revtype(repo.rev, True))
                    if depth:
                        err = err + ("\nThe --depth option might prevent fetching the whole revision tree and checking out %s." % (repo.revtype(repo.rev, True)))
                    if ignore:
                        warning(err)
                    else:
                        error(err, e[0])
            break
        except ProcessException:
            if os.path.isdir(repo.path):
                rmtree_readonly(repo.path)
    else:
        err = "Unable to clone repository (%s)" % url
        if ignore:
            warning(err)
        else:
            error(err, 1)

    repo.sync()

    if top: # This helps sub-commands to display relative paths to the imported program
        cwd_root = repo.path

    with cd(repo.path):
        deploy(ignore=ignore, depth=depth, protocol=protocol, top=False)

    if top:
        Program(repo.path).post_action()


# Deploy command
@subcommand('deploy',
    dict(name=['-I', '--ignore'], action='store_true', help='Ignore errors related to cloning and updating.'),
    dict(name='--depth', nargs='?', help='Number of revisions to fetch from the remote repository. Default: all revisions.'),
    dict(name='--protocol', nargs='?', help='Transport protocol for the source control management. Supported: https, http, ssh, git. Default: inferred from URL.'),
    help='Import missing dependencies in the current program or library.')
def deploy(ignore=False, depth=None, protocol=None, top=True):
    repo = Repo.fromrepo()
    repo.ignores()

    for lib in repo.libs:
        if os.path.isdir(lib.path):
            if lib.check_repo():
                with cd(lib.path):
                    update(lib.rev, ignore=ignore, depth=depth, protocol=protocol, top=False)
        else:
            import_(lib.fullurl, lib.path, ignore=ignore, depth=depth, protocol=protocol, top=False)
            repo.ignore(relpath(repo.path, lib.path))

    if top:
        Program(repo.path).post_action()


# Add library command
@subcommand('add',
    dict(name='url', help='URL of the library'),
    dict(name='path', nargs='?', help='Destination name or path. Default: current folder.'),
    dict(name=['-I', '--ignore'], action='store_true', help='Ignore errors related to cloning and updating.'),
    dict(name='--depth', nargs='?', help='Number of revisions to fetch from the remote repository. Default: all revisions.'),
    dict(name='--protocol', nargs='?', help='Transport protocol for the source control management. Supported: https, http, ssh, git. Default: inferred from URL.'),
    help='Add a library and its dependencies into the current %s or specified destination path.' % cwd_type)
def add(url, path=None, ignore=False, depth=None, protocol=None, top=True):
    repo = Repo.fromrepo()

    lib = Repo.fromurl(url, path)
    import_(lib.fullurl, lib.path, ignore=ignore, depth=depth, protocol=protocol, top=False)
    repo.ignore(relpath(repo.path, lib.path))
    lib.sync()

    lib.write()
    repo.add(lib.lib)

    if top:
        Program(repo.path).post_action()


# Remove library
@subcommand('remove',
    dict(name='path', help='Local library name or path'),
    help='Remove specified library and its dependencies from the current %s.' % cwd_type)
def remove(path):
    repo = Repo.fromrepo()
    if not Repo.isrepo(path):
        error("Could not find library in path (%s)" % path, 1)

    lib = Repo.fromrepo(path)
    action("Removing library \"%s\" in \"%s\"" % (lib.name, lib.path))
    rmtree_readonly(lib.path)
    repo.remove(lib.lib)
    repo.unignore(relpath(repo.path, lib.path))


# Publish command
@subcommand('publish',
    dict(name=['-A', '--all'], action='store_true', help='Publish all branches, including new. Default: push only the current branch.'),
    help='Publish current %s and its dependencies to associated remote repository URLs.' % cwd_type)
def publish(all=None, top=True):
    if top:
        action("Checking for local modifications...")

    repo = Repo.fromrepo()
    if repo.is_local:
        error(
            "%s \"%s\" in \"%s\" is a local repository.\nPlease associate it with a remote repository URL before attempting to publish.\n"
            "Read more about %s repositories here:\nhttp://developer.mbed.org/handbook/how-to-publish-with-%s/" % ("Program" if top else "Library", repo.name, repo.path, repo.scm.name, repo.scm.name), 1)

    for lib in repo.libs:
        if lib.check_repo():
            with cd(lib.path):
                progress()
                publish(False, all)

    sync(recursive=False)

    if repo.dirty():
        action("Uncommitted changes in %s \"%s\" in \"%s\"" % (repo.pathtype(repo.path), repo.name, repo.path))
        raw_input('Press enter to commit and publish: ')
        repo.commit()

    try:
        outgoing = repo.outgoing()
        if outgoing > 0:
            action("Pushing local repository \"%s\" to remote \"%s\"" % (repo.name, repo.url))
            repo.publish(all)
    except ProcessException as e:
        if e[0] != 1:
            raise e


# Update command
@subcommand('update',
    dict(name='rev', nargs='?', help='Revision, tag or branch'),
    dict(name=['-C', '--clean'], action='store_true', help='Perform a clean update and discard all local changes. WARNING: This action cannot be undone. Use with caution.'),
    dict(name=['-F', '--force'], action='store_true', help='Enforce the original layout and will remove any local libraries and also libraries containing uncommitted or unpublished changes. WARNING: This action cannot be undone. Use with caution.'),
    dict(name=['-I', '--ignore'], action='store_true', help='Ignore errors related to unpublished libraries, unpublished or uncommitted changes, and attempt to update from associated remote repository URLs.'),
    dict(name='--depth', nargs='?', help='Number of revisions to fetch from the remote repository. Default: all revisions.'),
    dict(name='--protocol', nargs='?', help='Transport protocol for the source control management. Supported: https, http, ssh, git. Default: inferred from URL.'),
    help='Update current %s and its dependencies from associated remote repository URLs.' % cwd_type)
def update(rev=None, clean=False, force=False, ignore=False, top=True, depth=None, protocol=None):
    if top and clean:
        sync()

    repo = Repo.fromrepo()
    # A copy of repo containing the .lib layout before updating
    repo_orig = Repo.fromrepo()

    if top and not rev and repo.isdetached():
        error(
            "This %s is in detached HEAD state, and you won't be able to receive updates from the remote repository until you either checkout a branch or create a new one.\n"
            "You can checkout a branch using \"%s checkout <branch_name>\" command before running \"mbed update\"." % (cwd_type, repo.scm.name), 1)

    if repo.is_local and not repo.rev:
        action("Skipping unpublished empty %s \"%s\"" % (
            cwd_type if top else cwd_dest,
            os.path.basename(repo.path) if top else relpath(cwd_root, repo.path)))
    else:
        # Fetch from remote repo
        action("Updating %s \"%s\" to %s" % (
            cwd_type if top else cwd_dest,
            os.path.basename(repo.path) if top else relpath(cwd_root, repo.path),
            repo.revtype(rev, True)))

        try:
            repo.update(rev, clean, repo.is_local)
        except ProcessException as e:
            err = "Unable to update \"%s\" to %s" % (repo.name, repo.revtype(rev, True))
            if depth:
                err = err + ("\nThe --depth option might prevent fetching the whole revision tree and checking out %s." % (repo.revtype(repo.rev, True)))
            if ignore:
                warning(err)
            else:
                error(err, e[0])

        repo.rm_untracked()
        if top and cwd_type == 'library':
            repo.sync()
            repo.write()

    # Compare library references (.lib) before and after update, and remove libraries that do not have references in the current revision
    for lib in repo_orig.libs:
        if not os.path.isfile(lib.lib) and os.path.isdir(lib.path): # Library reference doesn't exist in the new revision. Will try to remove library to reproduce original structure
            gc = False
            with cd(lib.path):
                lib_repo = Repo.fromrepo(lib.path)
                gc, msg = lib_repo.can_update(clean, force)
            if gc:
                action("Removing library \"%s\" (obsolete)" % (relpath(cwd_root, lib.path)))
                rmtree_readonly(lib.path)
                repo.unignore(relpath(repo.path, lib.path))
            else:
                if ignore:
                    warning(msg)
                else:
                    error(msg, 1)

    # Reinitialize repo.libs() to reflect the library files after update
    repo.sync()

    # Recheck libraries as their urls might have changed
    for lib in repo.libs:
        if os.path.isdir(lib.path) and Repo.isrepo(lib.path):
            lib_repo = Repo.fromrepo(lib.path)
            if lib.url != lib_repo.url: # Repository URL has changed
                gc = False
                with cd(lib.path):
                    gc, msg = lib_repo.can_update(clean, force)
                if gc:
                    action("Removing library \"%s\" (changed URL). Will add from new URL." % (relpath(cwd_root, lib.path)))
                    rmtree_readonly(lib.path)
                    repo.unignore(relpath(repo.path, lib.path))
                else:
                    if ignore:
                        warning(msg)
                    else:
                        error(msg, 1)

    # Import missing repos and update to revs
    for lib in repo.libs:
        if not os.path.isdir(lib.path):
            import_(lib.fullurl, lib.path, ignore=ignore, depth=depth, protocol=protocol, top=False)
            repo.ignore(relpath(repo.path, lib.path))
        else:
            with cd(lib.path):
                update(lib.rev, clean, force, ignore=ignore, top=False)

    if top:
        Program(repo.path).post_action()


# Synch command
@subcommand('sync',
    help='Synchronize dependency references (.lib files) in the current %s.' % cwd_type)
def sync(recursive=True, keep_refs=False, top=True):
    if top and recursive:
        action("Synchronizing dependency references...")

    repo = Repo.fromrepo()
    repo.ignores()

    for lib in repo.libs:
        if os.path.isdir(lib.path):
            lib.check_repo()
            lib.sync()
            lib.write()
            repo.ignore(relpath(repo.path, lib.path))
            progress()
        else:
            if not keep_refs:
                action("Removing reference \"%s\" -> \"%s\"" % (lib.name, lib.fullurl))
                repo.remove(lib.lib)
                repo.unignore(relpath(repo.path, lib.path))

    for root, dirs, files in os.walk(repo.path):
        dirs[:] = [d for d in dirs  if not d.startswith('.')]
        files[:] = [f for f in files if not f.startswith('.')]

        for d in list(dirs):
            if not Repo.isrepo(os.path.join(root, d)):
                continue

            lib = Repo.fromrepo(os.path.join(root, d))
            if os.path.isfile(lib.lib):
                dirs.remove(d)
                continue

            dirs.remove(d)
            lib.write()
            repo.ignore(relpath(repo.path, lib.path))
            repo.add(lib.lib)
            progress()

    repo.sync()

    if recursive:
        for lib in repo.libs:
            if lib.check_repo():
                with cd(lib.path):
                    sync(keep_refs=keep_refs, top=False)

    # Update the .lib reference in the parent repository
    if top and cwd_type == "library":
        repo = Repo.fromrepo()
        repo.write()


# List command
@subcommand('ls',
    dict(name=['-a', '--all'], action='store_true', help='List repository URL and revision pairs'),
    dict(name=['-I', '--ignore'], action='store_true', help='Ignore errors related to missing libraries.'),
    help='View the current %s dependency tree.' % cwd_type)
def list_(all=False, prefix='', p_path=None, ignore=False):
    repo = Repo.fromrepo()
    print prefix + (relpath(p_path, repo.path) if p_path else repo.name), '(%s)' % ((repo.fullurl if all else repo.rev) or 'no revision')

    for i, lib in enumerate(sorted(repo.libs, key=lambda l: l.path)):
        if prefix:
            nprefix = prefix[:-3] + ('|  ' if prefix[-3] == '|' else '   ')
        else:
            nprefix = ''
        nprefix += '|- ' if i < len(repo.libs)-1 else '`- '

        if lib.check_repo(ignore):
            with cd(lib.path):
                list_(all, nprefix, repo.path, ignore=ignore)


# Command status for cross-SCM status of repositories
@subcommand('status',
    dict(name=['-I', '--ignore'], action='store_true', help='Ignore errors related to missing libraries.'),
    help='Show status of the current %s and its dependencies.' % cwd_type)
def status_(ignore=False):
    repo = Repo.fromrepo()
    if repo.dirty():
        action("Status for \"%s\":" % repo.name)
        print repo.status()

    for lib in repo.libs:
        if lib.check_repo(ignore):
            with cd(lib.path):
                status_(ignore)


# Compile command which invokes the mbed OS native build system
@subcommand('compile',
    dict(name=['-t', '--toolchain'], help='Compile toolchain. Example: ARM, uARM, GCC_ARM, IAR'),
    dict(name=['-m', '--mcu'], help='Compile target. Example: K64F, NUCLEO_F401RE, NRF51822...'),
    dict(name='--source', action='append', help='Source directory. Default: . (current dir)'),
    dict(name='--build', help='Build directory. Default: .build/'),
    dict(name='--library', dest='compile_library', action='store_true', help='Compile the current %s as a static library.' % cwd_type),
    dict(name='--tests', dest='compile_tests', action='store_true', help='Compile tests in TESTS directory.'),
    dict(name='--test_spec', dest="test_spec", help="Destination path for a test spec file that can be used by the Greentea automated test tool. (Default is 'test_spec.json')"),
    help='Compile program using the native mbed OS build system.')
def compile(toolchain=None, mcu=None, source=False, build=False, compile_library=False, compile_tests=False, test_spec="test_spec.json"):
    args = remainder
    # Gather remaining arguments
    args = remainder
    # Find the root of the program
    program = Program(os.getcwd(), True)
    # Remember the original path. this is needed for compiling only the libraries and tests for the current folder.
    orig_path = os.getcwd()

    with cd(program.path):
        tools_dir = os.path.abspath(program.get_tools())
        target = program.get_mcu(mcu)
        tchain = program.get_toolchain(toolchain)
        macros = program.get_macros()

        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.abspath(program.path)

    if not source or len(source) == 0:
        source = [os.path.relpath(program.path, orig_path)]

    if compile_tests:
        # Compile tests
        if not build:
            build = os.path.join(os.path.relpath(program.path, orig_path), '.build/tests', target, tchain)

        popen(['python', '-u', os.path.join(tools_dir, 'test.py')]
              + list(chain.from_iterable(izip(repeat('-D'), macros)))
              + ['-t', tchain, '-m', target]
              + list(chain.from_iterable(izip(repeat('--source'), source)))
              + ['--build', build]
              + ['--test-spec', test_spec]
              + (['-v'] if verbose else [])
              + args,
              env=env)
    elif compile_library:
        # Compile as a library (current dir is default)
        if not build:
            build = os.path.join(os.path.relpath(program.path, orig_path), '.build', 'libraries', os.path.basename(orig_path), target, tchain)

        popen(['python', '-u', os.path.join(tools_dir, 'build.py')]
              + list(chain.from_iterable(izip(repeat('-D'), macros)))
              + ['-t', tchain, '-m', target]
              + list(chain.from_iterable(izip(repeat('--source'), source)))
              + ['--build', build]
              + (['-v'] if verbose else [])
              + args,
              env=env)
    else:
        # Compile as application (root is default)
        if not build:
            build = os.path.join(os.path.relpath(program.path, orig_path), '.build', target, tchain)

        popen(['python', '-u', os.path.join(tools_dir, 'make.py')]
              + list(chain.from_iterable(izip(repeat('-D'), macros)))
              + ['-t', tchain, '-m', target]
              + list(chain.from_iterable(izip(repeat('--source'), source)))
              + ['--build', build]
              + (['-v'] if verbose else [])
              + args,
              env=env)


# Test command
@subcommand('test',
    dict(name=['-l', '--list'], dest='tlist', action='store_true', help='List all of the available tests'),
    help='Find and build tests in a program and its libraries.')
def test(tlist=False):
    # Gather remaining arguments
    args = remainder
    # Find the root of the program
    program = Program(os.getcwd(), True)
    # Change directories to the program root to use mbed OS tools
    with cd(program.path):
        tools_dir = program.get_tools()

        # Prepare environment variables
        env = os.environ.copy()
        env['PYTHONPATH'] = '.'
        if tlist:
            # List all available tests (by default in a human-readable format)
            try:
                popen(['python', '-u', os.path.join(tools_dir, 'test.py'), '-l'] + args, env=env)
            except ProcessException:
                error('Failed to run test script')


# Export command
@subcommand('export',
    dict(name=['-i', '--ide'], help='IDE to create project files for. Example: UVISION,DS5,IAR', required=True),
    dict(name=['-m', '--mcu'], help='Export for target MCU. Example: K64F, NUCLEO_F401RE, NRF51822...'),
    help='Generate project files for desktop IDEs for the current program.')
def export(ide=None, mcu=None):
    # Gather remaining arguments
    args = remainder
    # Find the root of the program
    program = Program(os.getcwd(), True)
    # Change directories to the program root to use mbed OS tools
    with cd(program.path):
        tools_dir = program.get_tools()
        target = program.get_mcu(mcu)
        macros = program.get_macros()

        env = os.environ.copy()
        env['PYTHONPATH'] = '.'
        popen(['python', '-u', os.path.join(tools_dir, 'project.py')]
              + list(chain.from_iterable(izip(repeat('-D'), macros)))
              + ['-i', ide, '-m', target, '--source=%s' % program.path]
              + args,
              env=env)


# Build system and exporters
@subcommand('target',
    dict(name='name', nargs='?', help='Default target name. Example: K64F, NUCLEO_F401RE, NRF51822...'),
    help='Set default target for the current program.')
def target_(name=None):
    return default_('target', name)

@subcommand('toolchain',
    dict(name='name', nargs='?', help='Default toolchain name. Example: ARM, uARM, GCC_ARM, IAR'),
    help='Set default toolchain for the current program.')
def toolchain_(name=None):
    return default_('toolchain', name)

# Generic config command
@subcommand('default',
    dict(name='name', help='Variable name. E.g. "target", "toolchain", "protocol"'),
    dict(name='value', nargs='?', help='Value. Will show the currently set default value for a variable if not specified.'),
    help='Set or get program default options.')
def default_(name, value=None):
    # Find the root of the program
    program = Program(os.getcwd())
    # Change current dir to program root
    with cd(program.path):
        var = str(name).upper()
        if value is None:
            value = program.get_cfg(var)
            action(('%s' % value) if value else 'No default %s set in program "%s"' % (name, program.name))
        else:
            program.set_cfg(var, value)
            action('%s now set as default %s in program "%s"' % (value, name, program.name))

# 'config' command (calls into tools/get_config.py)
@subcommand('config',
    dict(name=['-t', '--toolchain'], help='Compile toolchain. Example: ARM, uARM, GCC_ARM, IAR'),
    dict(name=['-m', '--mcu'], help='Compile target. Example: K64F, NUCLEO_F401RE, NRF51822...'),
    dict(name='--source', action='append', help='Source directory. Default: . (current dir)'),
    dict(name='--prefix', action='append', help='Restrict listing to parameters that have this prefix'),
    help='Display the project configuration.')
def config(toolchain=None, mcu=None, source=False, prefix=None):
    # Find the root of the program
    program = Program(os.getcwd(), True)
    # Remember the original path. this is needed for compiling only the libraries and tests for the current folder.
    orig_path = os.getcwd()

    with cd(program.path):
        mbed_tools_path = program.get_tools_dir()
        if not mbed_tools_path:
            error('The mbed tools were not found in "%s". \n Run `mbed deploy` to install dependencies and tools. ' % program.path, -1)
        tools_dir = os.path.abspath(mbed_tools_path)

        if not os.path.isfile(os.path.join(tools_dir, 'get_config.py')):
            error("'get_config_py' not found in tools/. Please update mbed-os to get the latest tools.", -1)

        target = mcu if mcu else program.get_cfg('TARGET')
        if target is None:
            error('Please specify compile target using the -m switch or set default target using command "target"', 1)

        tchain = toolchain if toolchain else program.get_cfg('TOOLCHAIN')
        if tchain is None:
            error('Please specify compile toolchain using the -t switch or set default toolchain using command "toolchain"', 1)

        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.abspath(program.path)

    if not source or len(source) == 0:
        source = [os.path.relpath(program.path, orig_path)]

    popen(['python', os.path.join(tools_dir, 'get_config.py')]
          + ['-t', tchain, '-m', target]
          + list(chain.from_iterable(izip(repeat('--source'), source)))
          + (['-v'] if verbose else [])
          + (list(chain.from_iterable(izip(repeat('--prefix'), prefix))) if prefix else []),
          env=env)

# Parse/run command
if len(sys.argv) <= 1:
    parser.print_help()
    sys.exit(1)

pargs, remainder = parser.parse_known_args()
status = 1

try:
    very_verbose = pargs.very_verbose
    verbose = very_verbose or pargs.verbose
    log('Working path \"%s\" (%s)' % (os.getcwd(), cwd_type))
    status = pargs.command(pargs)
except ProcessException as e:
    error(
        "\"%s\" returned error code %d.\n"
        "Command \"%s\" in \"%s\"" % (e[1], e[0], e[2], e[3]), e[0])
except OSError as e:
    if e[0] == errno.ENOENT:
        error(
            "Could not detect one of the command-line tools.\n"
            "You could retry the last command with \"-v\" flag for verbose output\n", e[0])
    else:
        error('OS Error: %s' % e[1], e[0])
except KeyboardInterrupt as e:
    error('User aborted!', 255)

sys.exit(status or 0)
