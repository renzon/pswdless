# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from google.appengine.ext import ndb
from base import GAETestCase
from gaegraph.business_base import DestinationsSearch
from mock import Mock
from mommygae import mommy
from pswdless import login, facade
from pswdless.login import CertifySiteCredentials, ValidateLoginCall, CreateLogin, ChangeLoginStatus, SendLoginEmail

# mocking i18n
from pswdless.model import Site, PswdUser, Login, LoginUser, LoginSite, LOGIN_CALL, LoginStatusArc, LOGIN_EMAIL, LoginStatus, PswdUserEmail, EmailUser, SiteUser
import settings
from web import task
from zen import router

login._ = lambda s: s


class CertifyCredentialsTests(GAETestCase):
    def test_id_not_existent(self):
        cmd = CertifySiteCredentials('1', 'foo', r'http://www.pswdless.appspot.com/foo?b=2&p=5')
        cmd.execute()
        self.assertIsNone(cmd.result)
        self.assertDictEqual({'site': 'Wrong site id or token'}, cmd.errors)

    def test_id_wrong_token(self):
        site = mommy.make_one(Site, domain='www.pswdless.appspot.com')
        site.put()
        cmd = CertifySiteCredentials(str(site.key.id()), site.token + "foo",
                                     r'http://www.pswdless.appspot.com/foo?b=2&p=5')
        cmd.execute()
        self.assertIsNone(cmd.result)
        self.assertDictEqual({'site': 'Wrong site id or token'}, cmd.errors)

    def test_success(self):
        site = mommy.make_one(Site, domain='www.pswdless.appspot.com')
        site.put()
        cmd = CertifySiteCredentials(str(site.key.id()), site.token,
                                     r'http://www.pswdless.appspot.com/foo?b=2&p=5')
        cmd.execute()
        self.assertIsNotNone(cmd.result, str(cmd.errors))
        self.assertEqual(site.key, cmd.result.key)

    def _buildCertifyCredentials(self, site, hook=r'http://www.pswdless.appspot.com/foo?b=2&p=5'):
        return CertifySiteCredentials(str(site.key.id()), site.token, hook)

    def _assert_hook_error(self, hook, error_dct):
        site = mommy.make_one(Site, domain='www.pswdless.appspot.com')
        site.put()
        cmd = self._buildCertifyCredentials(site, hook) # ends with co instead of com
        cmd.execute()
        self.assertIsNone(cmd.result)
        self.assertDictEqual(error_dct, cmd.errors)

    def test_wrong_domain(self):
        self._assert_hook_error(r'https://www.pswdless.appspot.co',
                                {'domain': "Invalid domain: www.pswdless.appspot.co"})

    def test_wrong_protocol(self):
        self._assert_hook_error(r'htt://www.pswdless.appspot.com', {'protocol': 'Only http or https allowed, not htt'})


class ValidateLoginCallTest(GAETestCase):
    def test_success(self):
        domain = 'pswd.com'
        site = mommy.make_one(Site, domain=domain)
        site.put()
        validate_cmd = ValidateLoginCall(site.key.id(), site.token, 'http://www.pswd.com/pswdless',
                                         user_email='foo@bar.com')
        validate_cmd.execute()
        self.assertIsNotNone(validate_cmd.user, validate_cmd.errors)
        self.assertIsNotNone(validate_cmd.site, validate_cmd.errors)
        self.assertEqual(site.key, validate_cmd.site.key, validate_cmd.errors)


class CreateLoginTests(GAETestCase):
    def test_success(self):
        site = mommy.make_one(Site)
        user = mommy.make_one(PswdUser)
        ndb.put_multi([site, user])
        create_login = CreateLogin(user, site, 'hook')
        create_login.execute()
        login = create_login.result
        self.assertIsNotNone(login)
        self.assertEqual(LOGIN_CALL, login.status)
        self.assertEqual('hook', login.hook)
        db_login = Login.query().get()
        self.assertEqual(db_login.key, login.key)


        def neighbor(cls):
            search = DestinationsSearch(cls, login)
            search.execute()
            self.assertEqual(1, len(search.result), cls)
            return search.result[0]

        n_user = neighbor(LoginUser)
        self.assertEqual(n_user.key, user.key)

        n_site = neighbor(LoginSite)
        self.assertEqual(n_site.key, site.key)

        login_status = neighbor(LoginStatusArc)
        self.assertEqual(LOGIN_CALL, login_status.label)


class SetupLoginTaskTests(GAETestCase):
    def test_success(self):
        site = mommy.make_one(Site, domain='appspot.com')
        user = mommy.make_one(PswdUser)
        ndb.put_multi([site, user])
        login.setup_locale = Mock()
        setup_task = facade.setup_login_task(str(site.key.id()), site.token, 'http://pswdless.appspot.com/return',
                                             str(user.key.id()), lang='pt_BR')
        task_obj = Mock()
        task_cls = Mock(return_value=task_obj)
        login.TaskQueueCommand = task_cls
        task_obj.commit = Mock(return_value=[])

        setup_task.execute()
        lg = Login.query().get()
        login.setup_locale.assert_called_once_with('pt_BR')
        self.assertIsNotNone(lg)
        task_cls.assert_called_once_with(settings.TASK_HERO, router.to_path(task.send_login_email),
                                         params={'login_id': str(lg.key.id()), 'lang': 'pt_BR'})
        task_obj.set_up.assert_called_once_with()
        task_obj.do_business.assert_called_once_with()
        task_obj.commit.assert_called_once_with()

        def neighbor(cls):
            search = DestinationsSearch(cls, lg)
            search.execute()
            self.assertEqual(1, len(search.result), cls)
            return search.result[0]

        n_user = neighbor(LoginUser)
        self.assertEqual(n_user.key, user.key)

        n_site = neighbor(LoginSite)
        self.assertEqual(n_site.key, site.key)

        login_status = neighbor(LoginStatusArc)
        self.assertEqual(LOGIN_CALL, login_status.label)


class ChangeLoginStatusTests(GAETestCase):
    def test_success(self):
        login = mommy.make_one(Login, status=LOGIN_CALL)
        login.put()
        cmd = ChangeLoginStatus(login.key.id(), LOGIN_EMAIL)
        cmd.execute()
        modified_login = cmd.result
        self.assertEqual(login.key, modified_login.key)
        login_db = login.key.get()
        self.assertEqual(LOGIN_EMAIL, login_db.status)
        search = DestinationsSearch(LoginStatusArc, login)
        search.execute()
        self.assertEqual(1, len(search.result))
        login_status = search.result[0]
        self.assertIsInstance(login_status, LoginStatus)
        self.assertEqual(LOGIN_EMAIL, login_status.label)


class SendEmailTests(GAETestCase):
    def test_success(self):
        # Mocks
        site = Site(domain='pswdless.appspot.com', token='t')
        user = PswdUser()
        email = PswdUserEmail(email='foo@bar.com')
        login = Login(status=LOGIN_CALL, hook='https://pswdless.appspot.com/foo')
        ndb.put_multi([site, user, email, login])

        # Arcs
        ndb.put_multi(
            [EmailUser(origin=email.key, destination=user.key), LoginUser(origin=login.key, destination=user.key),
             LoginSite(origin=login.key, destination=site.key)])

        callback_flag = Mock()

        def callback(*args):
            callback_flag()
            zipped = zip([login, site, user, email], args)
            for tpl in zipped:
                self.assertEqual(type(tpl[0]), type(tpl[1]))
                self.assertEqual(tpl[0].key, tpl[1].key)

        send_email = facade.send_login_email(str(login.key.id()), callback)
        send_email.execute()

        # Login changes
        login_db = login.key.get()
        self.assertEqual(LOGIN_EMAIL, login_db.status)
        search = DestinationsSearch(LoginStatusArc, login)
        search.execute()
        self.assertEqual(1, len(search.result))
        login_status = search.result[0]
        self.assertIsInstance(login_status, LoginStatus)
        self.assertEqual(LOGIN_EMAIL, login_status.label)

        # Site User creation
        user_search = DestinationsSearch(SiteUser, site)
        user_search.execute()
        self.assertEqual(1, len(user_search.result))
        db_user = user_search.result[0]
        self.assertEqual(user.key, db_user.key)

        # Callback call
        callback_flag.assert_called_once_with()
