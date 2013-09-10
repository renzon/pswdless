# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from urlparse import urlparse

from google.appengine.api import users
from webapp2_extras.i18n import gettext as _

from gaegraph.model import to_node_key
from os import urandom
from gaebusiness.business import Command
from pswdless.model import Site, SiteOwner
from pswdless.users import FindOrCreateUser
import settings


class SaveSite(Command):
    def __init__(self, user, url):
        super(SaveSite, self).__init__()
        self._user = user
        self._url = url
        self._to_commit = None


    def set_up(self):
        parse_result=urlparse(self._url)
        domain = parse_result.netloc.split(':')[0] or self._url
        token = urandom(16).encode('hex')
        self.result = Site(domain=domain, token=token)
        self._future = self.result._put_async()

    def do_business(self, stop_on_error=False):
        site_key = self._future.get_result()
        self._to_commit = SiteOwner(origin=to_node_key(self._user), destination=site_key)

    def commit(self):
        return self._to_commit


class InitialSetup(Command):
    def set_up(self):
        google_user = users.get_current_user()
        if google_user:
            if users.is_current_user_admin():
                find_user=FindOrCreateUser(google_user.email())
                find_user.execute()
                self._save_site=SaveSite(find_user.result,settings.APP_HOST)
                self._save_site.set_up()
            else:
                self.add_error('user', _('You have no admin permission'))
        else:
            self.add_error('user', _('Login with your Google account'))

    def do_business(self, stop_on_error=False):
        if not self.errors:
            self._save_site.do_business()
            self.result=self._save_site.result

    def commit(self):
        if not self.errors:
            return self._save_site.commit()


