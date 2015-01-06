# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from config.template_middleware import TemplateResponse
from gaebusiness.business import CommandExecutionException
from gaecookie.decorator import no_csrf
from gaegraph.business_base import DestinationsSearch
from gaepermission.decorator import login_not_required
from pswdless import facade, languages
from pswdless.model import LoginSite


@login_not_required
@no_csrf
def index(_handler, _resp, lang, signed_ticket_id):
    languages.setup_locale(lang)
    cmd = facade.validate_login_link(signed_ticket_id, _handler.redirect)
    try:
        cmd.execute()
    except CommandExecutionException:
        _resp.status_code = 400
        values = {'errors': cmd.errors, 'site': None}
        if cmd.result:
            search = DestinationsSearch(LoginSite, cmd.result)
            search.execute()
            if search.result:
                values['site'] = search.result[0]
        return TemplateResponse(values, "login_error.html")


# def check_detail(_handler, _resp, ticket):
# url = settings.APP_HOME + router.to_path(rest.detail)
#     cmd = facade.log_user_in(ticket, _resp, url)
#     cmd.execute()
#     if not cmd.errors:
#         _handler.redirect('/')
