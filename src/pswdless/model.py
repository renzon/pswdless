# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

#Abstraction for classes that can be searchable on site
from google.appengine.ext import ndb
from gaegraph.model import Node, Arc


class Searchable(Node):
    pass


class Site(Searchable):
    domain = ndb.StringProperty(required=True)
    token = ndb.StringProperty(required=True)


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
