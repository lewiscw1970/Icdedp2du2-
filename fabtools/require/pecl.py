from fabtools.pecl import is_installed, install, uninstall


def extension(name, version=None, force=False):
    if not is_installed(name):
        install(name, version, force)


def extensions(ext_list):
    ext_list = [ext for ext in ext_list if not is_installed(ext)]
    if ext_list:
        for extension in ext_list:
            install(extension)


def noextension(name):
    if is_installed(name):
        uninstall(name)
