from fabtools import require
from fabtools.utils import run_as_root


def add_repo(repo_file_url):
    require.rpm.package('yum-utils')
    run_as_root('yum-config-manager --add-repo %(repo_file_url)s' % locals())


def enable_repo(repo_id):
    require.rpm.package('yum-utils')
    run_as_root('yum-config-manager --enable %(repo_id)s' % locals())


def disable_repo(repo_id):
    require.rpm.package('yum-utils')
    run_as_root('yum-config-manager --disable %(repo_id)s' % locals())
