# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from pswdclient import facade
from pswdless.security import xsrf


@xsrf
def index(_handler, _resp):
    facade.log_user_out(_resp).execute()
    _handler.redirect('/')
