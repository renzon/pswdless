# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from base import GAETestCase
from gaebusiness.business import CommandExecutionException
from gaegraph.business_base import DestinationsSearch
from gaegraph.model import to_node_key
from mock import Mock
from pswdless import sites, users, facade
from pswdless.model import SiteOwner
from pswdless.sites import SaveSite
from pswdless.users import FindOrCreateUser

import settings
# mocking i18n
users._ = lambda s: s
sites._ = lambda s: s


class FindCurrentSiteTests(GAETestCase):
    def test_success(self):
        users_mock = Mock()
        google_user = Mock()
        user_email = 'foo@bar.com'
        google_user.email = Mock(return_value=user_email)
        users_mock.get_current_user = Mock(return_value=google_user)
        users_mock.is_current_user_admin = Mock(return_value=True)
        sites.users = users_mock
        setup = facade.initial_setup()
        setup.execute()
        site = setup.result

        find = facade.find_current_site()
        find.execute()
        self.assertEqual(site.key, find.result.key)


class SaveSiteTests(GAETestCase):
    def test_success(self, url='http://www.mydomain.com', domain='www.mydomain.com'):
        find_user = FindOrCreateUser('foo@bar.com')
        find_user.execute()
        user = find_user.result
        save_site = SaveSite(user, url)
        save_site.execute()
        site = save_site.result
        self.assertEqual(domain, site.domain)
        self.assertIsNotNone(site.token)
        search = DestinationsSearch(SiteOwner, user)
        search.execute()
        self.assertListEqual([site.key], [s.key for s in search.result])

    def test_success_with_naked_domain(self):
        self.test_success('pswd.appspot.com', 'pswd.appspot.com')


class InitialSetupTests(GAETestCase):
    def test_success(self):
        users_mock = Mock()
        google_user = Mock()
        user_email = 'foo@bar.com'
        google_user.email = Mock(return_value=user_email)
        users_mock.get_current_user = Mock(return_value=google_user)
        users_mock.is_current_user_admin = Mock(return_value=True)
        sites.users = users_mock
        setup = facade.initial_setup()
        setup.execute()
        site = setup.result
        self.assertEqual(settings.APP_HOST, site.domain)
        find_user = FindOrCreateUser(user_email)
        find_user.execute()
        user = find_user.result
        search = DestinationsSearch(SiteOwner, to_node_key(user))
        search.execute()
        user_sites = search.result
        self.assertListEqual([site.key], [s.key for s in user_sites])


    def test_google_user_not_logged(self):
        users_mock = Mock()
        users_mock.get_current_user = Mock(return_value=None)
        sites.users = users_mock
        setup = facade.initial_setup()
        self.assertRaises(CommandExecutionException, setup.execute)
        self.assertIsNone(setup.result)
        self.assertDictEqual({'user': 'Login with your Google account'}, setup.errors)


    def test_google_user_not_admin(self):
        users_mock = Mock()
        users_mock.get_current_user = Mock(return_value=True)
        users_mock.is_current_user_admin = Mock(return_value=False)
        sites.users = users_mock
        setup = facade.initial_setup()
        self.assertRaises(CommandExecutionException, setup.execute)
        self.assertIsNone(setup.result)
        self.assertDictEqual({'user': 'You have no admin permission'}, setup.errors)
