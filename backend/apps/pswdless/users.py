# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from google.appengine.api import memcache
from google.appengine.ext import ndb
from webapp2_extras.i18n import gettext as _

from gaebusiness.business import Command, CommandParallel, CommandExecutionException
from gaegraph.business_base import DestinationsSearch, NodeSearch
from gaepermission import facade


class FindOrCreateUser(CommandParallel):
    def __init__(self, email):
        self.email = email
        super(FindOrCreateUser, self).__init__(facade.get_user_by_email(self.email))

    def do_business(self):
        super(FindOrCreateUser, self).do_business()
        user = self.result
        if not user:
            try:
                cmd = facade.save_user_cmd(self.email, self.email)
                self.result = cmd()
            except CommandExecutionException:
                self.errors.update(cmd.errors)


class FindUserById(NodeSearch):
    def do_business(self, stop_on_error=False):
        super(FindUserById, self).do_business()
        if self.result is None:
            self.add_error('user', _('User not found'))


class FindUserByIdOrEmail(Command):
    def __init__(self, id=None, email=None):
        super(FindUserByIdOrEmail, self).__init__()
        if id:
            self.find_command = FindUserById(id)
        elif email:
            self.find_command = FindOrCreateUser(email)
        else:
            self.add_error('params', _('One of user id or email must be present'))

    def set_up(self):
        if not self.errors:
            self.find_command.set_up()


    def do_business(self):
        if not self.errors:
            self.find_command.do_business()
            self.result = self.find_command.result
            self.errors = self.find_command.errors
        return self.errors

    def commit(self):
        if not self.errors:
            return self.find_command.commit()
