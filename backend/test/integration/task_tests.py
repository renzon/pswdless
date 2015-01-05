# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from google.appengine.ext import ndb, testbed
import webapp2

from base import GAETestCase
from pswdless.model import Site, PswdUser, PswdUserEmail, Login, LOGIN_CALL, EmailUser, LoginSite, LoginUser
import tmpl
from web import task


# workaround so i18n work on test (http://stackoverflow.com/questions/14960944/using-webapp2-i18n-in-unit-tests)
app = webapp2.WSGIApplication()
request = webapp2.Request({})
request.app = app
app.set_globals(app=app, request=request)


class SendLoginEmailTests(GAETestCase):
    def test_success(self):
        mail_stub = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)
        # Mocks
        site = Site(domain='pswdless.appspot.com', token='t')
        user = PswdUser()
        email = PswdUserEmail(email='foo@bar.com')
        login = Login(status=LOGIN_CALL, hook='https://pswdless.appspot.com/foo')
        ndb.put_multi([site, user, email, login])
        task._ = lambda s: s

        # Arcs
        ndb.put_multi(
            [EmailUser(origin=email.key, destination=user.key), LoginUser(origin=login.key, destination=user.key),
             LoginSite(origin=login.key, destination=site.key)])

        task.send_login_email(tmpl.render, str(login.key.id()), 'pt_BR')
        messages = mail_stub.get_sent_messages(to='foo@bar.com')
        self.assertEqual(1, len(messages))
