# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from google.appengine.api import taskqueue

from google.appengine.api.mail import send_mail_to_admins

from gaebusiness.gaeutil import ModelSearchCommand
from gaecookie.decorator import no_csrf
from gaegraph.business_base import SingleOriginSearch
from gaegraph.model import to_node_key
from gaepermission.decorator import login_not_required
from gaepermission.model import MainUser
from pswdless.model import PswdUser, EmailUser
import settings
from tekton.router import to_path


class UserSearch(ModelSearchCommand):
    def __init__(self, start_cursor=None):
        super(UserSearch, self).__init__(PswdUser.query_by_creation(), 1, start_cursor, 0, False, False)


@no_csrf
@login_not_required
def tasks(cursor=None):
    cmd = UserSearch(cursor)
    user = cmd()
    if user:
        user = user[0]
        email = SingleOriginSearch(EmailUser, user)().email
        MainUser(name=email, email=email, key=to_node_key(user), creation=user.creation).put()
        path = to_path(tasks, cmd.cursor.urlsafe())
        taskqueue.add(url=path)
    else:
        send_mail_to_admins(settings.SENDER_EMAIL, 'Migration End', 'Migration end')
