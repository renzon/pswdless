# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from gaegraph.business_base import DestinationsSearch
from pswdless import facade,languages
from pswdless.model import LoginSite
from routes import rest
import settings
from tekton import router




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
