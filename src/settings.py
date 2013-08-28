# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from google.appengine.api import app_identity

APP_NAME = 'Password-less'
APP_HOST = app_identity.get_default_version_hostname()
LOCALES = ['en_US', 'pt_BR']
DEFAULT_LOCALE = 'en_US'
LANG_COOKIE = 'pswdlang'
