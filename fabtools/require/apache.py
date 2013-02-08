import tempita

from fabtools import apache
from fabtools.require.deb import package
from fabtools.require.service import started
from fabtools.require.files import file as _file


def server():
    package('apache2')
    started('apache2')


def site(site_name, template_contents=None, template_source=None, enabled=True, check_config=True, **kwargs):
    server()

    config_filename = '/etc/apache2/sites-available/%s.conf' % site_name
    if template_contents:
        tmpl = tempita.Template(template_contents)
    elif template_source:
        f = open(template_source, 'r')
        tmpl = tempita.Template(f.read())
        f.close()

    _file(
        path=config_filename,
        contents=tmpl.substitute(kwargs)
    )

    if enabled:
        apache.enable_site(site_name)
