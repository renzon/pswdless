# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

#Abstraction for classes that can be searchable on site
from google.appengine.ext import ndb
from gaegraph.model import Node, Arc, to_node_key


class Searchable(Node):
    pass


class Site(Searchable):
    domain = ndb.StringProperty(required=True)
    token = ndb.StringProperty(required=True)

    @classmethod
    def find_by_domain(cls, domain):
        return cls.query(cls.domain == domain).order(cls.creation)

# User data
class PswdUser(Searchable):
    pass


class PswdUserEmail(Searchable):
    email = ndb.StringProperty(required=True)

    @classmethod
    def find_by_email(cls, email):
        return cls.query(cls.email == email.strip())


class EmailUser(Arc):
    pass


class SiteOwner(Arc):
    pass


class SiteUser(Arc):
    pass

# Login Process data. Records the login process and its status and history

LOGIN_CALL = 'CALL'
LOGIN_EMAIL = 'EMAIL'
LOGIN_CLICK = 'CLICK'
LOGIN_DETAIL = 'DETAIL'

LOGIN_STATUSES = [LOGIN_CALL, LOGIN_EMAIL, LOGIN_CLICK, LOGIN_DETAIL]


class Login(Searchable):
    hook = ndb.TextProperty(required=True)
    status = ndb.StringProperty(required=True, choices=LOGIN_STATUSES)


class LoginStatus(Node):
    label = ndb.StringProperty(required=True, indexed=False, choices=LOGIN_STATUSES)


class LoginUser(Arc):
    @classmethod
    def find_last(cls, user):
        return cls.query(cls.destination == to_node_key(user)).order(-cls.creation)


class LoginSite(Arc):
    pass


class LoginStatusArc(Arc):
    pass


