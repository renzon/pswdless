# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging


def index(_write_tmpl,email):
    logging.info(email)
    _write_tmpl("templates/login.html")

