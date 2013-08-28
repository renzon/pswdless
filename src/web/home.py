# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from webapp2_extras.i18n import gettext as _


def index(_write_tmpl):
    _write_tmpl("templates/home.html")
