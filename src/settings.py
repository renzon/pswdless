# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from google.appengine.api import app_identity

APP_NAME = 'Passwordless'
APP_HOST = app_identity.get_default_version_hostname() or r'pswdless.appspot.com'
APP_HOME = 'http://' + APP_HOST if APP_HOST.startswith('localhost') else 'https://' + APP_HOST
LOCALES = ['en_US', 'pt_BR']
DEFAULT_LOCALE = 'en_US'
LANG_COOKIE = 'pswdlang'
XSRF_TOKEN = 'XSRF-RANDOM'
# 6 hour in seconds
XSRF_TOKEN_EXPIRATION = 21600
# this name is default for Angular JS (http://docs.angularjs.org/api/ng.$http)
#  So if you are using it, don't change this name
XSRF_ANGULAR_COOKIE = 'XSRF-TOKEN'
XSRF_ANGULAR_AJAX_COOKIE = 'X-XSRF-TOKEN'

EMAIL_SENDER = 'Passwordless<login@pswdless.appspotmail.com>'

# See queue.yaml for configuration
TASK_HERO = 'hero'

LINK_EXPIRATION = 3600  # link must be used on 3600 seconds (1 hour)
