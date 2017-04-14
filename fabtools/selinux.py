from fabric.api import sudo, abort
from fabtools.utils import grep
from fabtools.editor import (Line, update_file)


def add_port(port_type, port):
    if not grep('semanage port -l',
                'http_port_t.*\s+{port}[\s+,\\n]'.format(port=port)):
        sudo("semanage port -a -t %(port_type)s -p tcp %(port)s" % locals())


def add_ports(type, ports):
    for port in ports:
        add_port(port_type='http_port_t', port=port)


def setsebool(selinux_boolean, value):
    result = sudo("getsebool {0}".format(selinux_boolean))
    if '--> on' in result and value == 0:
        sudo("setsebool -P {0} 0".format(selinux_boolean))
    elif '--> off' in result and value == 1:
        sudo("setsebool -P {0} 1".format(selinux_boolean))


def set_policy(policy='unset', permanent=True):
    allowed_policies = ['permissive', 'enforcing', 'disabled']
    if policy not in allowed_policies:
        msg = 'SELinux policy unspecified. Specify one of: {0}'.format(
                ', '.join(allowed_policies))
        abort(msg)
    if policy == 'permissive':
        sudo('setenforce 0')
    elif policy == 'enforcing':
        sudo('setenforce 1')

    if permanent:
        lines = [Line('^SELINUX[ \t]*=.*$', '=.*', '={0}'.format(policy))]
        update_file('/etc/sysconfig/selinux', lines, use_sudo=True)


def set_permissive(permanent=True):
    set_policy('permissive', permanent)


def set_enforcing(permanent=True):
    set_policy('enforcing', permanent)


def set_disabled(permanent=True):
    set_policy('disabled', permanent)
