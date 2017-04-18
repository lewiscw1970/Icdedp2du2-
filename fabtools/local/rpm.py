from fabric.api import settings, hide
from fabtools.local.utils import run_as_root, run


MANAGER = 'yum -y --color=never'


def is_installed(pkg_name):
    with settings(
            hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
        res = run("rpm --query %(pkg_name)s" % locals())
        if res.succeeded:
            return True
        return False


def install(packages, repos=None, yes=None, options=None):
    manager = MANAGER
    if options is None:
        options = []
    elif isinstance(options, str):
        options = [options]
    if not isinstance(packages, basestring):
        packages = " ".join(packages)
    if repos:
        for repo in repos:
            options.append('--enablerepo=%(repo)s' % locals())
    options = " ".join(options)
    if isinstance(yes, str):
        run_as_root('yes %(yes)s | %(manager)s %(options)s install %(packages)s' % locals())
    else:
        run_as_root('%(manager)s %(options)s install %(packages)s' % locals())


def uninstall(packages, options=None):
    manager = MANAGER
    if options is None:
        options = []
    elif isinstance(options, str):
        options = [options]
    if not isinstance(packages, basestring):
        packages = " ".join(packages)
    options = " ".join(options)
    run_as_root('%(manager)s %(options)s remove %(packages)s' % locals())


