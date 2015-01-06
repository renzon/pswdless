# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from config.template_middleware import TemplateResponse
from gaecookie.decorator import no_csrf
from gaepermission.decorator import login_required


@login_required
@no_csrf
def index():
    return TemplateResponse(template_path="sites.html")

