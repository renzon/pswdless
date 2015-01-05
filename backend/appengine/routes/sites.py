# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from pswdless.security import logged


@logged
def index(_write_tmpl):
    _write_tmpl("templates/sites.html")

