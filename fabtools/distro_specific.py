from functools import update_wrapper
from fabric.state import env
import fabtools

def current_distro():
    return fabtools.distros[env.host]

registry = {}

class DistroSpecific(object):
    def __init__(self):
        self.default = None
        self.distros = {}
    def __call__(self, *args):
        function = self.distros.get(current_distro(), self.default)
        if function is None:
            raise TypeError("no match")
        return function(*args)
    def register(self, distro, function):
        if distro in self.distros:
            raise TypeError("duplicate registration")
        if distro:
            self.distros[distro] = function
        else:
            self.default = function


def distro(distro=None):
    def register(function):
        key = '%s#%s'%(function.__module__, function.__name__)
        ds = registry.get(key)
        if ds is None:
            ds = registry[key] = DistroSpecific()
            update_wrapper(ds, function)
        ds.register(distro, function)
        return ds
    return register


def check_distro_support(distro):
    for name, function in registry.iteritems():
        if not distro in function.distros:
            print '%s does not support %s'%(name, distro)
