# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

from google.appengine.api import mail
from webapp2_extras.i18n import gettext as _

from pswdless import facade
from pswdless.languages import setup_locale
from routes.login import redirect
import settings
from tekton import router
from gaecookie import facade as gaecookie_facade


def setup(_resp, _handler):
    _resp.write('Setup disabled. You can enable by removing the coments on web.setup.py')
    # setup_cmd=facade.initial_setup()
    # setup_cmd.execute()
    # if setup_cmd.result:
    # _resp.write('Initial setup ok')
    # else:
    #     google_user=users.get_current_user()
    #     if google_user:
    #         _resp.write(setup_cmd.errors)
    #     else:
    #         return_url=router.to_path(setup)
    #         login_url=users.create_login_url(return_url)
    #         _handler.redirect(login_url)


def send_login_email(_render, login_id, lang):
    logging.info(login_id)
    logging.info(login_id)
    setup_locale(lang)

    def send(login, site, user):
        cmd = gaecookie_facade.sign('ticket', login.key.id())
        cmd.execute()
        signed = cmd.result
        link = settings.APP_HOME + router.to_path(redirect, lang, signed)
        values = {'APP_NAME': settings.APP_NAME, 'site': site.domain, 'login_link': link}
        body = _render('login_email.txt', values)
        subject = _('%(site)s Login Link') % {'site': site.domain}
        logging.info(user)
        logging.info(body)
        mail.send_mail(settings.SENDER_EMAIL,
                       user.email,
                       subject,
                       body)

    facade.send_login_email(login_id, send).execute()
