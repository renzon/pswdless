# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from urlparse import urlparse

from google.appengine.api import users, memcache
from webapp2_extras.i18n import gettext as _

from gaegraph.business_base import DestinationsSearch
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
        parse_result = urlparse(self._url)
        domain = parse_result.netloc.split(':')[0] or self._url
        if domain:
            token = urandom(16).encode('hex')
            self.result = Site(domain=domain, token=token)
            self._future = self.result._put_async()
        else:
            self.add_error('domain', _('Domain should not be empty'))

    def do_business(self, stop_on_error=False):
        if not self.errors:
            site_key = self._future.get_result()
            self._to_commit = SiteOwner(origin=to_node_key(self._user), destination=site_key)

    def commit(self):
        if not self.errors:
            return self._to_commit


class FindUserSites(DestinationsSearch):
    def __init__(self, user):
        super(FindUserSites, self).__init__(SiteOwner, user)


class UpdateSite(DestinationsSearch):
    def __init__(self, user, site, domain=None, token=False):
        super(UpdateSite, self).__init__(SiteOwner, user, user=user, site_key=to_node_key(site), domain=domain,
                                         token=token)

    def do_business(self, stop_on_error=True):
        super(UpdateSite, self).do_business(stop_on_error)

        def find_site(site_key):
            for site in self.result:
                if site.key == site_key:
                    return site

        site_found = find_site(self.site_key)
        self.result = site_found
        if site_found:
            if self.domain:
                parse_result = urlparse(self.domain)
                domain = parse_result.netloc.split(':')[0]
                site_found.domain = domain or self.domain
            elif self.token:
                site_found.token = urandom(16).encode('hex')
            self._site_future = site_found.put_async()
        else:
            self.add_error('credentials', _('Site not found'))

    def commit(self):
        if not self.errors:
            self._site_future.get_result()


class InitialSetup(Command):
    def set_up(self):
        google_user = users.get_current_user()
        if google_user:
            if users.is_current_user_admin():
                find_user = FindOrCreateUser(google_user.email())
                find_user.execute()
                self._save_site = SaveSite(find_user.result, settings.APP_HOST)
                self._save_site.set_up()
            else:
                self.add_error('user', _('You have no admin permission'))
        else:
            self.add_error('user', _('Login with your Google account'))

    def do_business(self, stop_on_error=False):
        if not self.errors:
            self._save_site.do_business()
            self.result = self._save_site.result

    def commit(self):
        if not self.errors:
            return self._save_site.commit()


class FindCurrentSite(Command):
    def set_up(self):
        try:
            self.result = memcache(settings.APP_HOST)
        except:
            pass
        if not self.result:
            self._future = Site.find_by_domain(settings.APP_HOST).get_async()

    def do_business(self, stop_on_error=False):
        if not self.result:
            self.result = self._future.get_result()
            memcache.set(settings.APP_HOST, self.result)
