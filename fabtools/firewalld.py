from fabric.api import sudo
from fabtools import systemd


def reload():
    cmd = 'firewall-cmd --reload'
    sudo(cmd)


def open_port(port, proto, zone='public', permanent=True, reload=True):
    cmd = ('firewall-cmd --zone={zone} --add-port={port}/{proto}'.format(
           zone=zone, port=port, proto=proto))
    if permanent:
        cmd += ' --permanent'
    sudo(cmd)
    if reload:
        reload()


def start():
    systemd.start(name='firewalld')


def stop():
    systemd.stop(name='firewalld')


def enable():
    systemd.enable(name='firewalld')


def disable():
    systemd.disable(name='firewalld')
