from fabtools import pythonz


def install(version='2.7.3', pip=True, virtualenv=True):
    if not pythonz.is_python_installed(version):
        pythonz.install(version)

    if pip:
        install_pip(version)

    if virtualenv:
        install_virtualenv(version)


def install_pip(version='2.7.3'):
    if not pythonz.is_pip_installed(version):
        pythonz.install_pip(version)


def install_virtualenv(version='2.7.3'):
    if not pythonz.is_virtualenv_installed(version):
        pythonz.install_virtualenv(version)
