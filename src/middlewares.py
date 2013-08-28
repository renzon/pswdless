# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from webapp2_extras import i18n
import settings


def setup_language(req, resp, next_process):
    locale=req.cookies.get(settings.LANG_COOKIE)

    if locale is None:
        locale = req.headers.get("Accept-Language", settings.DEFAULT_LOCALE).split(",")[0]
        locale = locale.replace("-", "_")
        if not (locale in settings.LOCALES):
            locale=settings.DEFAULT_LOCALE
        resp.set_cookie(settings.LANG_COOKIE,locale)

    i18n.get_i18n().set_locale(locale)
    next_process()




MIDLEWARE_LIST = [setup_language]
