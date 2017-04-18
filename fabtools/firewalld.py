from fabric.api import sudo
from fabtools import systemd


def reload():
    cmd = 'firewall-cmd --reload'
    sudo(cmd)


def open_port(port, proto, zone='public', permanent=True, reload_fw=True):
    cmd = ('firewall-cmd --zone={zone} --add-port={port}/{proto}'.format(
           zone=zone, port=port, proto=proto))
    if permanent:
        cmd += ' --permanent'
    sudo(cmd)
    if reload_fw:
        reload()


def start():
    systemd.start('firewalld')


def stop():
    systemd.stop('firewalld')


def enable():
    systemd.enable('firewalld')


def disable():
    systemd.disable('firewalld')
