from fabtools.local.rpm import (
    install,
    is_installed,
    uninstall,
)


def package(pkg_name, repos=None, yes=None, options=None):
    if not is_installed(pkg_name):
        install(pkg_name, repos, yes, options)


def packages(pkg_list, repos=None, yes=None, options=None):
    pkg_list = [pkg for pkg in pkg_list if not is_installed(pkg)]
    if pkg_list:
        install(pkg_list, repos, yes, options)


def nopackage(pkg_name, options=None):
    if is_installed(pkg_name):
        uninstall(pkg_name, options)


def nopackages(pkg_list, options=None):
    pkg_list = [pkg for pkg in pkg_list if is_installed(pkg)]
    if pkg_list:
        uninstall(pkg_list, options)
