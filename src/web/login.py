# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from pswdclient import facade as pswdclient_facade
from pswdless import facade
from pswdless.security import xsrf
import settings
from web import rest
from zen import router


@xsrf
def index(_write_tmpl, _req, email):
    hook = settings.APP_HOME + router.to_path(check_detail)
    lang = _req.cookies.get(settings.LANG_COOKIE)
    current_site_cmd=facade.find_current_site()
    current_site_cmd.execute()
    site=current_site_cmd.result
    url_login = settings.APP_HOME + router.to_path(rest.login)
    cmd = pswdclient_facade.send_login_email(site.key.id(), site.token, hook, email, lang=lang, url_login=url_login)
    cmd.execute()
    if not cmd.errors:
        _write_tmpl("templates/login.html")


def redirect(signed_ticket_id):
    pass


def check_detail(_resp, **kwargs):
    _resp.write('Sucessful loged in')
