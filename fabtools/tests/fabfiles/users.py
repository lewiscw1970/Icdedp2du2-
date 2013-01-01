from __future__ import with_statement

from fabric.api import *
from fabtools import require
import fabtools


@task
def users():
    """
    Check user creation
    """
    # create default user
    fabtools.user.create('default')
    assert fabtools.user.exists('default')

    # create no-login user
    fabtools.user.create('no-login', disabled_login=True)
    assert fabtools.user.exists('no-login')

    # require that a user exist
    require.user('foo')
    assert fabtools.user.exists('foo')
