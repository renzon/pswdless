# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from google.appengine.api.app_identity import app_identity
from gaecookie.middleware import CSRFMiddleware, CSRFInputToDependency
from locale_app.middleware import LocaleMiddleware
from tekton.gae.middleware.json_middleware import JsonResponseMiddleware
from config.template_middleware import TemplateMiddleware, TemplateWriteMiddleware
from tekton.gae.middleware.email_errors import EmailMiddleware
from tekton.gae.middleware.parameter import RequestParamsMiddleware
from tekton.gae.middleware.redirect import RedirectMiddleware
from tekton.gae.middleware.router_middleware import RouterMiddleware, ExecutionMiddleware
from tekton.gae.middleware.webapp2_dependencies import Webapp2Dependencies
from gaepermission.middleware import LoggedUserMiddleware, PermissionMiddleware


APP_NAME = 'Passwordless'
APP_HOST = app_identity.get_default_version_hostname() or r'pswdless.appspot.com'
APP_HOME = 'http://' + APP_HOST if APP_HOST.startswith('localhost') else 'https://' + APP_HOST

# See queue.yaml for configuration
TASK_HERO = 'hero'

LINK_EXPIRATION = 60  # link must be used on 3600 seconds (1 hour)


APP_URL = APP_HOME
SENDER_EMAIL = 'Passwordless<login@pswdless.appspotmail.com>'
DEFAULT_LOCALE = 'en_US'
DEFAULT_TIMEZONE = 'US/Eastern'
LOCALES = ['en_US', 'pt_BR']
TEMPLATE_404_ERROR = 'base/404.html'
TEMPLATE_400_ERROR = 'base/400.html'
MIDDLEWARE_LIST = [LoggedUserMiddleware,
                   TemplateMiddleware,
                   EmailMiddleware,
                   Webapp2Dependencies,
                   RequestParamsMiddleware,
                   CSRFInputToDependency,
                   LocaleMiddleware,
                   RouterMiddleware,
                   CSRFMiddleware,
                   PermissionMiddleware,
                   ExecutionMiddleware,
                   TemplateWriteMiddleware,
                   JsonResponseMiddleware,
                   RedirectMiddleware]


