"""
Vagrant helpers
===============
"""
from __future__ import with_statement

from fabric.api import env, hide, local, settings, task


def ssh_config(name=''):
    """
    Get the SSH parameters for connecting to a vagrant VM.
    """
    with settings(hide('running')):
        output = local('vagrant ssh-config %s' % name, capture=True)

    config = {}
    for line in output.splitlines()[1:]:
        key, value = line.strip().split(' ', 2)
        config[key] = value
    return config


def list_vms():
    """
    Count how many vagrant VMs are running and list hostnames
    """
    with settings(hide('running')):
        output = local('vagrant status | grep running', capture=True)

    vms = []
    for line in output.splitlines():
        vms.append(line.strip().split(' ', 2)[0])
    return vms


def _settings_dict(config):
    settings = {}

    user = config['User']
    hostname = config['HostName']
    port = config['Port']

    # Build host string
    host_string = "%s@%s:%s" % (user, hostname, port)

    settings['user'] = user
    settings['hosts'] = [host_string]
    settings['host_string'] = host_string

    # Strip leading and trailing double quotes introduced by vagrant 1.1
    settings['key_filename'] = config['IdentityFile'].strip('"')

    settings['forward_agent'] = (config.get('ForwardAgent', 'no') == 'yes')
    settings['disable_known_hosts'] = True

    return settings


@task
def vagrant(*names):
    """
    Run the following tasks on a vagrant box.

    First, you need to import this task in your ``fabfile.py``::

        from fabric.api import *
        from fabtools.vagrant import vagrant

        @task
        def some_task():
            run('echo hello')

    Then you can easily run tasks on your current/all Vagrant box::

        $ fab vagrant some_task

    Or on specific Vagrant boxes::

        $ fab vagrant:machine1,machine2 some_task

    """
    vms = list_vms()
    # Run on all if no specifics given
    if len(names) == 0:
        names = vms
    hosts = [x for x in names if x in vms]
    for vm in hosts:
        config = ssh_config(vm)
        extra = _settings_dict(config)
        # This works as the only uniqueness is the host string
        save_hosts = env.hosts
        save_hosts.append(extra["host_string"])
        extra["hosts"] = save_hosts
        env.update(extra)


def vagrant_settings(name='', *args, **kwargs):
    """
    Context manager that sets a vagrant VM
    as the remote host.

    Use this context manager inside a task to run commands
    on your current Vagrant box::

        from fabtools.vagrant import vagrant_settings

        with vagrant_settings():
            run('hostname')
    """
    config = ssh_config(name)

    extra_args = _settings_dict(config)
    kwargs.update(extra_args)

    return settings(*args, **kwargs)
