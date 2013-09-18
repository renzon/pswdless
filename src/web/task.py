# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from google.appengine.api import mail
from webapp2_extras.i18n import gettext as _
from pswdclient import facade as pswdclient

from pswdless import facade
from pswdless.languages import setup_locale
import settings
from web.login import redirect
from zen import router


def setup(_resp, _handler):
    _resp.write('Setup disabled. You can enable by removing the coments on web.setup.py')
    # setup_cmd=facade.initial_setup()
    # setup_cmd.execute()
    # if setup_cmd.result:
    #     _resp.write('Initial setup ok')
    # else:
    #     google_user=users.get_current_user()
    #     if google_user:
    #         _resp.write(setup_cmd.errors)
    #     else:
    #         return_url=router.to_path(setup)
    #         login_url=users.create_login_url(return_url)
    #         _handler.redirect(login_url)


def send_login_email(_render, login_id, lang):
    setup_locale(lang)

    def send(login, site, user, email):
        cmd = pswdclient.sign_dct('ticket', login.key.id())
        cmd.execute()
        signed = cmd.result
        link = settings.APP_HOME + router.to_path(redirect, signed)
        values = {'APP_NAME': settings.APP_NAME, 'site': site, 'login_link': link}
        body = _render('templates/login_email.txt', values)
        mail.send_mail(settings.EMAIL_SENDER, email.email,
                       _('%(site)s Login Link') % {'site': site.domain},
                       body)

    facade.send_login_email(login_id, send).execute(True)
