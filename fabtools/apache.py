from fabtools.files import is_link
from fabtools._utils import root_run


def is_started():
    """
    Check if Apache is started
    """
    ret = root_run('apache2ctl status')
    return ('Apache Server Status' in ret)


def is_stopped():
    """
    Check if Apache is stopped
    """
    ret = root_run('apache2ctl status')
    return ('Apache Server Status' not in ret)


def start():
    root_run('apache2ctl start')


def stop():
    root_run('apache2ctl stop')


def restart():
    root_run('apache2ctl restart')


def _get_link_filename(site_name):
    return '/etc/apache2/sites-enabled/%s' % site_name


def _get_site_name(site_name):
    if site_name not in ('default', 'default-ssl'):
        site_name += '.conf'

    return site_name


def is_site_enabled(site_name):
    return is_link(_get_link_filename(_get_site_name(site_name)))


def enable_site(site_name):
    if not is_site_enabled(site_name):
        root_run('a2ensite %s.conf' % _get_site_name(site_name))


def disable_site(site_name):
    if is_site_enabled(site_name):
        root_run('a2dissite %s.conf' % _get_site_name(site_name))
