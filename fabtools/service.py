"""
System services
===============

This module provides low-level tools for managing system services,
using the ``service`` command. It supports both `upstart`_ services
and traditional SysV-style ``/etc/init.d/`` scripts.

.. _upstart: http://upstart.ubuntu.com/

"""
from __future__ import with_statement

from fabric.api import *
from fabtools.distro_specific import distro

@distro('deb')
def is_running(service):
    """
    Check if a service is running.

    ::

        import fabtools

        if fabtools.service.is_running('foo'):
            print "Service foo is running!"
    """
    with settings(hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
        res = sudo('service %(service)s status' % locals())
        return res.succeeded


@distro('arch')
def is_running(service):
    with settings(hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
        res = sudo('rc.d list %(service)s --started' % locals())
        return bool(res)


@distro('deb')
def start(service):
    """
    Start a service.

    ::

        import fabtools

        # Start service if it is not running
        if not fabtools.service.is_running('foo'):
            fabtools.service.start('foo')
    """
    sudo('service %(service)s start' % locals())


@distro('arch')
def start(service):
    sudo('rc.d start %(service)s' % locals())


@distro('deb')
def stop(service):
    """
    Stop a service.

    ::

        import fabtools

        # Stop service if it is running
        if fabtools.service.is_running('foo'):
            fabtools.service.stop('foo')
    """
    sudo('service %(service)s stop' % locals())


@distro('arch')
def stop(service):
    sudo('rc.d stop %(service)s' % locals())


@distro('deb')
def restart(service):
    """
    Restart a service.

    ::

        import fabtools

        # Start service, or restart it if it is already running
        if fabtools.service.is_running('foo'):
            fabtools.service.restart('foo')
        else:
            fabtools.service.start('foo')
    """
    sudo('service %(service)s restart' % locals())


@distro('arch')
def restart(service):
    sudo('rc.d restart %(service)s' % locals())
