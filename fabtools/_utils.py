from fabric.api import run, sudo, env


def root_run(cmd):
    if env['user'] == 'root':
        return run(cmd)
    else:
        return sudo(cmd)
