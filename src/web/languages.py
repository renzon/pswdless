# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from pswdless.security import xsrf
import settings


def index(_write_tmpl):
    _write_tmpl("templates/languages.html")

@xsrf
def change(_handler,_resp, lang):
   _resp.set_cookie(settings.LANG_COOKIE,lang)
   _handler.redirect('/')


