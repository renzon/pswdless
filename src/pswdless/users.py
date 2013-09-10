# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from google.appengine.api import memcache
from google.appengine.ext import ndb

from webapp2_extras.i18n import gettext as _

from gaebusiness.business import Command
from gaegraph.business_base import NeighborsSearch
from pswdless.model import PswdUserEmail, EmailUser, PswdUser
import re


class FindOrCreateUser(Command):
    def _cache_key(self):
        return FindOrCreateUser.__name__ + self.email

    def __init__(self, email):
        super(FindOrCreateUser, self).__init__()
        self._to_commit = None
        if not email:
            self.add_error('email', _('Email is required'))
        elif re.match(r'[^@]+@[^@]+\.[^@]+', email):
            self.email = email.strip()
        else:
            self.add_error('email', _('Email is invalid'))

    def set_up(self):
        if not self.errors:
            try:
                self.result = memcache.get(self._cache_key())
                if self.result:
                    return
            except:
                pass
            self._future = PswdUserEmail.find_by_email(self.email).get_async()


    def do_business(self, stop_on_error=False):
        if not self.errors and not self.result:
            pswd_email = self._future.get_result()
            if pswd_email:
                search = NeighborsSearch(EmailUser, pswd_email)
                search.execute()
                self.result = search.result[0]
            else:
                pswd_email = PswdUserEmail(email=self.email)
                self.result = PswdUser()
                ndb.put_multi([pswd_email, self.result])
                memcache.add(self._cache_key(),self.result)
                self._to_commit = EmailUser(origin=pswd_email.key, destination=self.result.key)

    def commit(self):
        return self._to_commit

