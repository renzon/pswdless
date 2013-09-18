# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from google.appengine.api import memcache
from google.appengine.ext import ndb

from webapp2_extras.i18n import gettext as _

from gaebusiness.business import Command
from gaegraph.business_base import DestinationsSearch, NodeSearch
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
                search = DestinationsSearch(EmailUser, pswd_email)
                search.execute()
                self.result = search.result[0]
            else:
                pswd_email = PswdUserEmail(email=self.email)
                self.result = PswdUser()
                ndb.put_multi([pswd_email, self.result])
                memcache.add(self._cache_key(), self.result)
                self._to_commit = EmailUser(origin=pswd_email.key, destination=self.result.key)

    def commit(self):
        return self._to_commit


class FindUserById(NodeSearch):
    def do_business(self, stop_on_error=False):
        super(FindUserById, self).do_business()
        if self.result is None:
            self.add_error('user', _('User not found'))


class FindUserByIdOrEmail(Command):
    def __init__(self, id=None, email=None):
        super(FindUserByIdOrEmail, self).__init__()
        if id:
            self.find_command=FindUserById(id)
        elif email:
            self.find_command=FindOrCreateUser(email)
        else:
            self.add_error('params',_('One of user id or email must be present'))

    def set_up(self):
        if not self.errors:
            self.find_command.set_up()


    def do_business(self, stop_on_error=False):
        if not self.errors:
            self.find_command.do_business(stop_on_error)
            self.result=self.find_command.result
            self.errors=self.find_command.errors
        return self.errors

    def commit(self):
        if not self.errors:
            return self.find_command.commit()
