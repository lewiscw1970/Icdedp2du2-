from fabric.api import sudo, abort, settings, hide
from fabric.contrib.files import exists


def is_installed(name):
    with settings(
            hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
        if sudo('pecl list | grep %(name)s' % locals()).succeeded:
            return True
        return False


def action(action=None, name=None, version=None, force=False):
    allowed_actions = ['install', 'uninstall', 'upgrade']
    if name is None:
        abort('Specify PHP extension name (PECL) name')
    if action not in allowed_actions:
        abort('Specify pecl action: {0}'.format(', '.join(allowed_actions)))
    if force:
        action += ' --force'
    if version is not None:
        name += '-{0}'.format(version)
    cmd = 'pecl {action} {name}'.format(action=action, name=name)
    sudo(cmd)


def install(name, version=None, force=False):
    # pecl has a bug and cannot see openssl libs installed in a 64bit system.
    # This is a workaround.
    if exists ('/usr/lib64/libssl.a') and not exists('/usr/lib/libssl.a'):
        sudo('ln -s /usr/lib64/libssl* /usr/lib/')
    prompts = {
        'OpenSSL install prefix (no to disable SSL support) [/usr] : ': '/usr'}
    with settings(prompts=prompts):
        action(action='install', name=name, version=version, force=force)


def uninstall(name):
    action(action='uninstall', name=name)


def upgrade(name):
    action(action='upgrade', name=name)

