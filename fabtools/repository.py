"""
Repositories
===============

This module provides helpers to manage a repository clone.

All the following commands assume you execute them in the repository directory.
"""

from fabric.api import run


def reset(vcs='git'):
    """
    Reset current repository to latest commit.
    """
    if vcs == 'git':
        run('git reset --hard')


def update(vcs='git', remote='origin', branch='master'):
    """
    Update code from remote repository
    """
    if vcs == 'git':
        run('git pull %s %s' % (remote, branch))


def branch(name, vcs='git'):
    """
    Change repository branch.
    """
    if vcs == 'git':
        run('git checkout -b %s' % name)
