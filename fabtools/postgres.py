"""
PostgreSQL users and databases
==============================

This module provides tools for creating PostgreSQL users and databases.

"""
from __future__ import with_statement

from datetime import datetime as _date

from pipes import quote
import posixpath
import fabtools
from fabric.api import abort, cd, hide, settings, sudo


def _run_as_pg(command):
    """
    Run command as 'postgres' user
    """
    with cd('~postgres'):
        return sudo(command, user='postgres')


def _port_option(port):
    """
    Return the option port if port passed
    """
    if port:
        return "-p %(port)s " % locals()
    else: 
        return None


def user_exists(name, port=None):
    """
    Check if a PostgreSQL user exists.
    """
    command_options = [
        '-t',
        '-A'
    ]
    port_option = _port_option(port)

    if port_option is not None:
        command_options.append(port_option)

    command_options = ' '.join(command_options)

    with settings(hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
        res = _run_as_pg('''psql %(command_options)s -c "SELECT COUNT(*) FROM pg_user WHERE usename = '%(name)s';"''' % locals())
    return (res == "1")


def create_user(name, password, superuser=False, createdb=False,
                createrole=False, inherit=True, login=True,
                connection_limit=None, encrypted_password=False, port=None):
    """
    Create a PostgreSQL user.

    Example::

        import fabtools

        # Create DB user if it does not exist
        if not fabtools.postgres.user_exists('dbuser'):
            fabtools.postgres.create_user('dbuser', password='somerandomstring')

        # Create DB user with custom options
        fabtools.postgres.create_user('dbuser2', password='s3cr3t',
            createdb=True, createrole=True, connection_limit=20)

    """
    options = [
        'SUPERUSER' if superuser else 'NOSUPERUSER',
        'CREATEDB' if createdb else 'NOCREATEDB',
        'CREATEROLE' if createrole else 'NOCREATEROLE',
        'INHERIT' if inherit else 'NOINHERIT',
        'LOGIN' if login else 'NOLOGIN',
    ]
    if connection_limit is not None:
        options.append('CONNECTION LIMIT %d' % connection_limit)
    password_type = 'ENCRYPTED' if encrypted_password else 'UNENCRYPTED'
    options.append("%s PASSWORD '%s'" % (password_type, password))
    options = ' '.join(options)

    command_options = [
        '-c'
    ]
    port_option = _port_option(port)

    if port_option is not None:
        command_options.append(port_option)

    command_options = ' '.join(command_options)

    _run_as_pg('''psql %(command_options)s "CREATE USER %(name)s %(options)s;"''' % locals())


def drop_user(name, port=None):
    """
    Drop a PostgreSQL user.

    Example::

        import fabtools

        # Remove DB user if it exists
        if fabtools.postgres.user_exists('dbuser'):
            fabtools.postgres.drop_user('dbuser')

    """
    command_options = [
        '-c'
    ]
    port_option = _port_option(port)

    if port_option is not None:
        command_options.append(port_option)

    command_options = ' '.join(command_options)

    _run_as_pg('''psql %(command_options)s "DROP USER %(name)s;"''' % locals())


def database_exists(name, port=None):
    """
    Check if a PostgreSQL database exists.
    """
    command_options = [
        '-d',
    ]
    port_option = _port_option(port)

    if port_option is not None:
        command_options.append(port_option)

    command_options = ' '.join(command_options)

    with settings(hide('running', 'stdout', 'stderr', 'warnings'),
                  warn_only=True):
        return _run_as_pg('''psql %(command_options)s %(name)s -c ""''' % locals()).succeeded


def create_database(name, owner, template='template0', encoding='UTF8',
                    locale='en_US.UTF-8', port=None):
    """
    Create a PostgreSQL database.

    Example::

        import fabtools

        # Create DB if it does not exist
        if not fabtools.postgres.database_exists('myapp'):
            fabtools.postgres.create_database('myapp', owner='dbuser')

    """
    command_options = []
    port_option = _port_option(port)

    if port_option is not None:
        command_options.append(port_option)
    command_options = ' '.join(command_options)

    _run_as_pg('''createdb %(command_options)s --owner %(owner)s --template %(template)s \
                  --encoding=%(encoding)s --lc-ctype=%(locale)s \
                  --lc-collate=%(locale)s %(name)s''' % locals())


def drop_database(name, port=None):
    """
    Delete a PostgreSQL database.

    Example::

        import fabtools

        # Remove DB if it exists
        if fabtools.postgres.database_exists('myapp'):
            fabtools.postgres.drop_database('myapp')

    """
    command_options = []
    port_option = _port_option(port)

    if port_option is not None:
        command_options.append(port_option)
    command_options = ' '.join(command_options)

    _run_as_pg('''dropdb %(command_options)s %(name)s''' % locals())


def create_schema(name, database, owner=None, port=None):
    """
    Create a schema within a database.
    """
    command_options = []
    port_option = _port_option(port)

    if port_option is not None:
        command_options.append(port_option)
    command_options = ' '.join(command_options)

    if owner:
        _run_as_pg('''psql %(command_options)s %(database)s -c "CREATE SCHEMA %(name)s AUTHORIZATION %(owner)s"''' % locals())
    else:
        _run_as_pg('''psql %(command_options)s %(database)s -c "CREATE SCHEMA %(name)s"''' % locals())
        

def dump_database(database, path='/var/backups/postgres', filename='', format='plain', port=None):
    """
    Generate a dump database to a remote destination path
    Example::

        import fabtools

        fabtools.postgres.dump_database('myapp', path='/var/backups/postgres', filename='myapp-backup.sql')
        # If not filename specified will be saved with the date file format: database-201312010000.sql
        fabtools.postgres.dump_database('myapp', path='/var/backups/postgres') 
        # If not path specified will be saved at '/var/backups/postgres'
        fabtools.postgres.dump_database('myapp')
        # You can scpecify the pg_dump's custom format (able to restore with pg_restore)
        fabtools.postgres.dump_database('myapp', format='custom')

    """
    command_options = []
    port_option = _port_option(port)

    if port_option is not None:
        command_options.append(port_option)

    command_options = ' '.join(command_options)

    if fabtools.files.is_dir(path):
        if database_exists(database):
                date = _date.today().strftime("%Y%m%d%H%M")
                if not filename:
                    filename = '%(database)s-%(date)s.sql' % locals()
                dest = quote(posixpath.join(path, filename))
                _run_as_pg('pg_dump %(command_options)s %(database)s --format=%(format)s --blobs --file=%(dest)s' % locals())
        else:
            abort('''Database does not exist: %(database)s''' % locals())
    else:
        abort('''Destination path does not exist: %(path)s''' % locals())


def restore_database(database, sqlfile='', port=None):
    """
    Restore a sql file to a database
    Example::

        import fabtools

        fabtools.postgres.restore_database('myapp', sqlfile='/var/backups/postgres/myapp-backup.sql')
    """
    command_options = []
    port_option = _port_option(port)

    if port_option is not None:
        command_options.append(port_option)
    command_options = ' '.join(command_options)

    if fabtools.files.is_file(sqlfile):
        if database_exists(database):
            _run_as_pg('''psql %(command_options)s %(database)s < %(sqlfile)s''' % locals())
        else:
            abort('''Database does not exist: %(database)s''' % locals())
    else:
        abort('''Sql file does not exist: %(sqlfile)s''' % locals())


def drop_database(name, port=None):
    """
    Drop a PostgreSQL database.

    Example::

        import fabtools

        # Drop DB if exist
        if fabtools.postgres.database_exists('myapp'):
            fabtools.postgres.drop_database('myapp')

    """
    command_options = []
    port_option = _port_option(port)

    if port_option is not None:
        command_options.append(port_option)
    command_options = ' '.join(command_options)

    _run_as_pg('''dropdb %(command_options)s%(name)s''' % locals())
