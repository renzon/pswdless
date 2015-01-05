# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import json

from gaegraph.business_base import DestinationsSearch
from pswdclient import facade as pswdclient_facade
from pswdless import facade, languages
from pswdless.model import LoginSite
from pswdless.security import xsrf
import settings
from web import rest
from zen import router


@xsrf
def index(_write_tmpl, _req, email):
    hook = settings.APP_HOME + router.to_path(check_detail)
    lang = _req.cookies.get(settings.LANG_COOKIE)
    current_site_cmd = facade.find_current_site()
    current_site_cmd.execute()
    site = current_site_cmd.result
    url_login = settings.APP_HOME + router.to_path(rest.login)
    cmd = pswdclient_facade.send_login_email(site.key.id(), site.token, hook, email, lang=lang, url_login=url_login)
    cmd.execute()
    if not cmd.errors:
        _write_tmpl("templates/login.html")
    else:
        msgs=json.loads(cmd.errors['msg'])
        _write_tmpl("templates/errors.html",{'errors':msgs})


def redirect(_handler, _resp, _write_tmpl, lang, signed_ticket_id):
    languages.setup_locale(lang)
    cmd = facade.validate_login_link(signed_ticket_id, _handler.redirect)
    cmd.execute()
    if cmd.errors:
        _resp.status_code = 400
        values = {'errors': cmd.errors, 'site': None}
        if cmd.result:
            search = DestinationsSearch(LoginSite, cmd.result)
            search.execute()
            if search.result:
                values['site'] = search.result[0]
        _write_tmpl("templates/login_error.html", values)


def check_detail(_handler, _resp, ticket):
    url = settings.APP_HOME + router.to_path(rest.detail)
    cmd = facade.log_user_in(ticket, _resp, url)
    cmd.execute()
    if not cmd.errors:
        _handler.redirect('/')
