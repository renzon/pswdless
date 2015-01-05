# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from google.appengine.ext import ndb, testbed
import webapp2

from base import GAETestCase
from config import template
from gaepermission.model import MainUser
from mommygae import mommy
from pswdless.model import Site,  Login, LOGIN_CALL, LoginSite, LoginUser
from routes import task


class SendLoginEmailTests(GAETestCase):
    def test_success(self):
        mail_stub = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)
        # Mocks
        email='foo@bar.com'
        site = Site(domain='pswdless.appspot.com', token='t')
        user = mommy.save_one(MainUser,email=email)
        login = Login(status=LOGIN_CALL, hook='https://pswdless.appspot.com/foo')
        ndb.put_multi([site, user, login])
        task._ = lambda s: s

        # Arcs
        ndb.put_multi(
            [LoginUser(origin=login.key, destination=user.key),
             LoginSite(origin=login.key, destination=site.key)])

        task.send_login_email(template.render, str(login.key.id()), 'pt_BR')
        messages = mail_stub.get_sent_messages(to='foo@bar.com')
        self.assertEqual(1, len(messages))
