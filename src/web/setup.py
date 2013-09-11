# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from google.appengine.api import users
from pswdless import facade
from zen import router


def index(_resp,_handler):
    _resp.write('Setup disabled. You can enable by removing the coments on web.setup.py')
    # setup_cmd=facade.initial_setup()
    # setup_cmd.execute()
    # if setup_cmd.result:
    #     _resp.write('Initial setup ok')
    # else:
    #     google_user=users.get_current_user()
    #     if google_user:
    #         _resp.write(setup_cmd.errors)
    #     else:
    #         return_url=router.to_path(index)
    #         login_url=users.create_login_url(return_url)
    #         _handler.redirect(login_url)
