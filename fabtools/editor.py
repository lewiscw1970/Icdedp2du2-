from collections import namedtuple
from fabric.contrib.files import sed
from functools import partial


Line = namedtuple("Line", "regex before after")


def update_line(path, regex, before, after, use_sudo=False):
    _sed = partial(sed, path, use_sudo=use_sudo)
    _sed(before=before, after=after, limit=regex)


def update_file(path, lines, use_sudo=False):
    """
    Example:

        path = '/etc/php.ini'
        lines = [
            Line('memory_limit', '= .*', '= 256M'),
            Line('session.gc_maxlifetime', '= .*', '= 7200'),
        ]
        update_file(path, lines, use_sudo=True)

    """
    for line in lines:
        update_line(path, line.regex, line.before, line.after, use_sudo)
