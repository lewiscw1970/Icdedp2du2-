"""
Require Repositories
===============

This module provides helpers to clone a repository.
"""

from fabric.api import run
from fabric.contrib import files
from fabric.colors import red

def extract_name(repo_uri, cvs='git'):
    """
    Extract infos from given repository URI. Infos are the repository and the
    CVS used by the repository. These informations are returned as a tuple.
    """
    name = ''
    if(cvs == 'git'):
        name = repo_uri.split("/")[-1]
        name = name.split('.')[0]
    else:
        print red('Cannot extract name from given URI')
    return name

def clone(repo_uri, cvs='git'):
    """
    Clone a repository from given URI.
    """
    repo_name = extract_name(repo_uri, cvs=cvs)

    if(cvs == 'git'):
        if not files.exists(repo_name):
            run('git clone %s' % repo_uri)
        else:
            print red('Repository %s is already present' % repo_name)
    else:
        print red('Your Concurrent Versions System is not supported.')
