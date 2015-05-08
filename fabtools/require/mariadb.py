"""
MariaDB
=====

This module provides high-level tools for installing a MariaDB server.
Use the MySQL module to create users and databases.
"""

from fabric.api import hide, prompt, settings

from fabtools.deb import is_installed, preseed_package
from fabtools.require.deb import package, key, source
from fabtools.require.service import started
from fabtools.system import distrib_codename

def server(version='10.0', password=None):
    """
    Require a MariaDB server to be installed and running.  'Version' is the high level MariaDB series
    available (See https://downloads.mariadb.com/files/MariaDB/repo).  Not all versions available for
    all Deb systems.  Double check availability at mariadb.org.

    Example::

        from fabtools import require

        require.mariadb.server(version='10.0', password='s3cr3t')

    """
    if version:
        pkg_name = 'mariadb-server-%s' % version
    else:
        pkg_name = 'mariadb-server'

    if not is_installed(pkg_name):
        key(keyid='0xcbcb082a1bb943db', keyserver='keyserver.ubuntu.com')
        source_url = 'http://ftp.osuosl.org/pub/mariadb/repo/%s/ubuntu' % version
        source('mariadb', source_url, distrib_codename(), 'main')

        if password is None:
            password = prompt('Please enter password for MariaDB user "root":')
        
        with settings(hide('running')):
            preseed_package(pkg_name, {
                'mysql-server/root_password': ('password', password),
                'mysql-server/root_password_again': ('password', password),
            })

        package(pkg_name)

    started('mysql')