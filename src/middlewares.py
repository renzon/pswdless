# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from webapp2_extras import i18n
from pswdless.security import extract_xsrf_token, generate_xsrf_token
import settings


def setup_language(req, resp, next_process):
    locale = req.cookies.get(settings.LANG_COOKIE)

    if locale is None:
        locale = req.headers.get("Accept-Language", settings.DEFAULT_LOCALE).split(",")[0]
        locale = locale.replace("-", "_")
        if not (locale in settings.LOCALES):
            locale = settings.DEFAULT_LOCALE
        resp.set_cookie(settings.LANG_COOKIE, locale)

    i18n.get_i18n().set_locale(locale)
    next_process()


def xsrf_cookie(req, resp, next_process):
    token = req.cookies.get(settings.XSRF_TOKEN)
    random_number = extract_xsrf_token(req)
    if random_number is None:
        token,random_number=generate_xsrf_token()
    resp.set_cookie(settings.XSRF_TOKEN, token, httponly=True)
    resp.set_cookie(settings.XSRF_ANGULAR_COOKIE, random_number, httponly=True)
    next_process()
    return token


MIDLEWARE_LIST = [setup_language, xsrf_cookie]
