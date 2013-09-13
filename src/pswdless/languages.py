# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from webapp2_extras import i18n
import settings


def setup_locale(locale):
    if not (locale in settings.LOCALES):
        locale = settings.DEFAULT_LOCALE
    i18n.get_i18n().set_locale(locale)
    return locale
