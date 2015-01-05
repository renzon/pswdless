# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from gaepermission.decorator import login_required


@login_required
def index(_write_tmpl):
    _write_tmpl("sites.html")

