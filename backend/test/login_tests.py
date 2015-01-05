# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from datetime import datetime, timedelta

from google.appengine.ext import ndb

from base import GAETestCase
from gaebusiness.business import CommandExecutionException
from gaegraph.business_base import DestinationsSearch
from mock import Mock
from mommygae import mommy
from pswdless import login, facade
from pswdless.login import CertifySiteCredentials, ValidateLoginCall, CreateLogin, ChangeLoginStatus, ValidateLoginLink
from gaepermission import facade as permission_facade
from gaecookie import facade as cookie_facade




# mocking i18n
from pswdless.model import Site, PswdUser, Login, LoginUser, LoginSite, LOGIN_CALL, LoginStatusArc, LOGIN_EMAIL, \
    LoginStatus, PswdUserEmail, EmailUser, SiteUser, LOGIN_CLICK, LOGIN_DETAIL
import settings
from routes import task
from tekton import router

login._ = lambda s: s


class CertifyCredentialsTests(GAETestCase):
    def test_id_not_existent(self):
        cmd = CertifySiteCredentials('1', 'foo', r'http://www.pswdless.appspot.com/foo?b=2&p=5')
        self.assertRaises(CommandExecutionException, cmd.execute)
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
        cmd = self._buildCertifyCredentials(site, hook)  # ends with co instead of com
        self.assertRaises(CommandExecutionException,cmd.execute)
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

    def test_spam(self):
        site = mommy.make_one(Site, domain='www.pswd.com')
        user = mommy.make_one(PswdUser)
        ndb.put_multi([site, user])
        create_login = CreateLogin(user, site, 'hook')
        create_login.execute()
        # time.sleep(3)  # giving time because eventual consistency
        validate_cmd = ValidateLoginCall(site.key.id(), site.token, 'http://www.pswd.com/pswdless',
                                         user.key.id())
        self.assertRaises(CommandExecutionException, validate_cmd.execute)
        self.assertDictEqual({'spam': 'Spam not allowed'}, validate_cmd.errors)

    def test_success_after_one_hour(self):
        site = mommy.make_one(Site, domain='www.pswd.com')
        user = mommy.make_one(PswdUser)
        ndb.put_multi([site, user])
        create_login = CreateLogin(user, site, 'hook')

        create_login.execute()
        lg = Login.query().get()
        lg.creation = datetime.now() - timedelta(hours=1, minutes=1)
        lg.put()

        validate_cmd = ValidateLoginCall(site.key.id(), site.token, 'http://www.pswd.com/pswdless',
                                         user.key.id())
        validate_cmd.execute()
        self.assertDictEqual({}, validate_cmd.errors)

    def _assert_succes_with_status(self, status):
        site = mommy.make_one(Site, domain='www.pswd.com')
        user = mommy.make_one(PswdUser)
        ndb.put_multi([site, user])
        create_login = CreateLogin(user, site, 'hook')
        create_login.execute()
        lg = Login.query().get()
        lg.status = status
        lg.put()
        validate_cmd = ValidateLoginCall(site.key.id(), site.token, 'http://www.pswd.com/pswdless',
                                         user.key.id())
        validate_cmd.execute()
        self.assertDictEqual({}, validate_cmd.errors)

    def test_success_with_click_status(self):
        self._assert_succes_with_status(LOGIN_CLICK)

    def test_success_with_DETAIL_status(self):
        self._assert_succes_with_status(LOGIN_DETAIL)


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
                                         params={'login_id': str(lg.key.id()), 'lang': 'pt_BR'}, countdown=4)
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


class ValidateLoginLinkTests(GAETestCase):
    def _assert_error(self, token):
        validate_cmd = ValidateLoginLink(token, None)
        self.assertRaises(CommandExecutionException, validate_cmd.execute)
        self.assertDictEqual({'ticket': 'Invalid Call'}, validate_cmd.errors)

    def _assert_wrong_status(self, status):
        login = Login(status=status, hook='https://pswdless.appspot.com/foo')
        login.put()
        cmd = cookie_facade.sign('ticket', login.key.id())
        cmd.execute()
        self._assert_error(cmd.result)

    def test_invalid_token(self):
        self._assert_error('invalid token')

    def test_already_clicked(self):
        self._assert_wrong_status(LOGIN_CLICK)

    def test_already_got_detail(self):
        self._assert_wrong_status(LOGIN_DETAIL)

    def test_not_existing_login(self):
        cmd = cookie_facade.sign('ticket', 2)
        cmd.execute()
        self._assert_error(cmd.result)

    def test_success(self, hook='https://pswdless.appspot.com/foo', expected_query_string='?ticket=%s'):
        lg = Login(status=LOGIN_EMAIL, hook=hook)
        lg.put()

        cmd = cookie_facade.sign('ticket', lg.key.id())
        cmd.execute()
        redirect_mock = Mock()
        validate_cmd = facade.validate_login_link(cmd.result, redirect_mock)
        validate_cmd.execute()
        self.assertDictEqual({}, validate_cmd.errors)
        login_db = validate_cmd.result
        self.assertEqual(lg.key, login_db.key)
        self.assertEqual(login_db.status, LOGIN_CLICK)
        search = DestinationsSearch(LoginStatusArc, login_db)
        search.execute()
        self.assertEqual(1, len(search.result))
        lg_status = search.result[0]
        self.assertIsInstance(lg_status, LoginStatus)
        self.assertEqual(lg_status.label, LOGIN_CLICK)
        redirect_mock.assert_called_once_with(hook + (expected_query_string % lg.key.id()))

    def test_hook_with_query_string(self):
        self.test_success('https://pswdless.appspot.com/foo?param1=1', '&ticket=%s')


