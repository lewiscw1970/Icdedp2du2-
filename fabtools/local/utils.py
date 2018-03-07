from fabric.api import local as local_run


def whoami():
    return local_run('whoami', capture=True)


def run_as_root(command, *args, **kwargs):
    """
    Run a local command as the root user.

    """
    if whoami() != 'root':
        command = 'sudo ' + command
    return local_run(command, *args, **kwargs)


def sudo(command, *args, **kwargs):
    command = 'sudo ' + command
    return local_run(command, *args, **kwargs)


def run(command, *args, **kwargs):
    return local_run(command, *args, **kwargs)
