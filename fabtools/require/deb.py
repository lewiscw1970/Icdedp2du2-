"""
Debian packages
===============

This module provides high-level tools for managing Debian/Ubuntu packages
and repositories.

"""

from fabric.utils import puts
from fabric.contrib.files import (
    contains,
    comment,
    uncomment,
)

from fabric.colors import green, yellow

from fabtools.deb import (
    add_apt_key,
    apt_key_exists,
    install,
    install_file,
    is_installed,
    is_version,
    uninstall,
    update_index,
    last_update_time,
    needs_update,
)
from fabtools.files import is_file, watch
from fabtools.system import distrib_codename, distrib_release
from fabtools.utils import run_as_root
from fabtools import system


def key(keyid, filename=None, url=None, keyserver='subkeys.pgp.net', update=False):
    """
    Require a PGP key for APT.

    ::

        from fabtools import require

        # Varnish signing key from URL
        require.deb.key('C4DEFFEB', url='http://repo.varnish-cache.org/debian/GPG-key.txt')

        # Nginx signing key from default key server (subkeys.pgp.net)
        require.deb.key('7BD9BF62')

        # From custom key server
        require.deb.key('7BD9BF62', keyserver='keyserver.ubuntu.com')

        # From file
        require.deb.key('7BD9BF62', filename='nginx.asc')

    """

    if not apt_key_exists(keyid):
        add_apt_key(keyid=keyid, filename=filename, url=url, keyserver=keyserver, update=update)


def source(name, uri, distribution, *components):
    """
    Require a package source.

    ::

        from fabtools import require

        # Official MongoDB packages
        require.deb.source('mongodb', 'http://downloads-distro.mongodb.org/repo/ubuntu-upstart', 'dist', '10gen')

    """

    from fabtools.require import file as require_file

    path = '/etc/apt/sources.list.d/%(name)s.list' % locals()
    components = ' '.join(components)
    source_line = 'deb %(uri)s %(distribution)s %(components)s\n' % locals()
    with watch(path) as config:
        require_file(path=path, contents=source_line, use_sudo=True)
    if config.changed:
        puts('Added APT repository: %s' % source_line)
        update_index()


def source_list(component):
    """
    Require a component in /etc/apt/sources.list uncommented.

    Example::
        
        from fabtools import require

        require.deb.source_list('partner')

    """
    regex = '^#\s{0,1}deb\s.*%(component)s.*$' % locals()
    if contains('/etc/apt/sources.list', text=regex, escape=False):
        uncomment('/etc/apt/sources.list', regex=regex, use_sudo=True, char='# ')


def nosource_list(component):
    """
    Require a component in /etc/apt/sources.list commented. See :py:func:`fabtools.require.deb.source_list`
    """
    regex = '^deb\s.*%(component)s.*$' % locals()
    if contains('/etc/apt/sources.list', text=regex, escape=False):
        comment('/etc/apt/sources.list', regex=regex, use_sudo=True, char='# ')


def ppa(name, auto_accept=True, keyserver=None):
    """
    Require a `PPA`_ package source.

    Example::

        from fabtools import require

        # Node.js packages by Chris Lea
        require.deb.ppa('ppa:chris-lea/node.js', keyserver='my.keyserver.com')

    .. _PPA: https://help.launchpad.net/Packaging/PPA
    """
    assert name.startswith('ppa:')

    user, repo = name[4:].split('/', 2)

    release = float(distrib_release())
    if release >= 12.04:
        repo = repo.replace('.', '_')
        auto_accept = '--yes' if auto_accept else ''
    else:
        auto_accept = ''

    if not isinstance(keyserver, basestring) and keyserver:
        keyserver = keyserver[0]
    if keyserver:
        keyserver = '--keyserver ' + keyserver
    else:
        keyserver = ''

    distrib = distrib_codename()
    source = '/etc/apt/sources.list.d/%(user)s-%(repo)s-%(distrib)s.list' % locals()

    if not is_file(source):
        package('python-software-properties')
        run_as_root('add-apt-repository %(auto_accept)s %(keyserver)s %(name)s' % locals(), pty=False)
        update_index()


def package(pkg_name, update=False, version=None, quiet=False):
    """
    Require a deb package to be installed.

    Example::

        from fabtools import require

        # Require a package
        require.deb.package('foo')

        # Require a specific version
        require.deb.package('firefox', version='11.0+build1-0ubuntu4')

    """
    _needs_update = needs_update(pkg_name)
    _is_installed = is_installed(pkg_name)

    if not _is_installed and _needs_update:
        install(pkg_name, update=update, version=version)

    if not quiet:
        if _needs_update:
            puts(yellow( 'Updating: %s' % pkg_name ))
        if _is_installed:
            puts(green( 'Already installed: %s' % pkg_name ))
        else:
            puts(yellow( 'Installing: %s' % pkg_name ))


def packages(pkg_list, update=False, quiet=False):
    """
    Require several deb packages to be installed.

    Example::

        from fabtools import require

        require.deb.packages([
            'foo',
            'bar',
            'baz',
        ])
    """
    pkg_list = [pkg for pkg in pkg_list if not is_installed(pkg) or needs_update(pkg)]
    if pkg_list:
        install(pkg_list, update)

        if not quiet:
            puts(yellow( 'Installing or upgrading packages: %s' % ' '.join(pkg_list) ))
 

def package_file(pkg_name, filename=None, version=None, directory='packages', quiet=False):
    """
    Require a deb file to be uploaded and installed on remote pc.
    1) Check if package is not installed
    2) Check if installed package *starts with* version
    3) Upload *directory/filename* to remote host
    4) Install */tmp/filename* on remote host
    
    Example::
        
        from fabtools import require
        
        # Set up package info
        pkg_name = 'tzdata'
        pkg_filename = 'tzdata_2014i-0ubuntu0.14.04_all.deb'
        pkg_version = '2014i'

        # Require package with name 'tzdata' and version '2014i' is installed
        require.deb.package_file(pkg_name=pkg_name, filename=pkg_filename, version=pkg_version)
    
    """
    from fabtools.require.files import file as _require_file
    from fabtools.deb import install_file, get_version
    from os.path import exists

    do_install = False

    if not is_installed(pkg_name) or (version and not is_version(pkg_name, version)):
        do_install = True

    if not quiet:
        message = 'name=%(pkg_name)s version=%(version)s filename=%(filename)s' % locals()
        if do_install:
            puts(yellow( 'Installing: %s' % message ))
        else:
            puts(green( 'Already installed: %s' % message ))

    if do_install:
        if exists('%(directory)s/%(filename)s' % locals()):
            _require_file(path='/tmp/%(filename)s' % locals(), source='%(directory)s/%(filename)s' % locals())
            install_file('/tmp/%(filename)s' % locals())
            return True
        else:
            puts('%(directory)s/%(filename)s does not exists' % locals())
            return False


def nopackage(pkg_name, quiet=False):
    """
    Require a deb package to be uninstalled.

    Example::

        from fabtools import require

        require.deb.nopackage('apache2')
    """
    if is_installed(pkg_name):
        uninstall(pkg_name)
        
        if not quiet:
            puts(yellow( 'Uninstalling package: %s' % pkg_name) )


def nopackages(pkg_list, quiet=False):
    """
    Require several deb packages to be uninstalled.

    Example::

        from fabtools import require

        require.deb.nopackages([
            'perl',
            'php5',
            'ruby',
        ])
    """
    pkg_list = [pkg for pkg in pkg_list if is_installed(pkg)]
    if pkg_list:
        uninstall(pkg_list)

        if not quiet:
            puts(yellow( 'Uninstalling packages: %s' % ' '.join(pkg_list) ))


def _to_seconds(var):
    sec = 0
    MINUTE = 60
    HOUR = 60 * MINUTE
    DAY = 24 * HOUR
    WEEK = 7 * DAY
    MONTH = 31 * DAY
    try:
        for key, value in var.items():
            if key in ('second', 'seconds'):
                sec += value
            elif key in ('minute', 'minutes'):
                sec += value * MINUTE
            elif key in ('hour', 'hours'):
                sec += value * HOUR
            elif key in ('day', 'days'):
                sec += value * DAY
            elif key in ('week', 'weeks'):
                sec += value * WEEK
            elif key in ('month', 'months'):
                sec += value * MONTH
            else:
                raise ValueError("Unknown time unit '%s'" % key)
        return sec
    except AttributeError:
        return var


def uptodate_index(quiet=True, max_age=86400):
    """
    Require an up-to-date package index.

    This will update the package index (using ``apt-get update``) if the last
    update occured more than *max_age* ago.

    *max_age* can be specified either as an integer (a value in seconds),
    or as a dictionary whose keys are units (``seconds``, ``minutes``,
    ``hours``, ``days``, ``weeks``, ``months``) and values are integers.
    The default value is 1 hour.

    Examples: ::

        from fabtools import require

        # Update index if last time was more than 1 day ago
        require.deb.uptodate_index(max_age={'day': 1})

        # Update index if last time was more than 1 hour and 30 minutes ago
        require.deb.uptodate_index(max_age={'hour': 1, 'minutes': 30})

    """

    from fabtools.require import file as require_file
    require_file('/etc/apt/apt.conf.d/15fabtools-update-stamp', contents='''\
APT::Update::Post-Invoke-Success {"touch /var/lib/apt/periodic/fabtools-update-success-stamp 2>/dev/null || true";};
''', use_sudo=True)

    if system.time() - last_update_time() > _to_seconds(max_age):
        update_index(quiet=quiet)
        return True
    else:
        return False
