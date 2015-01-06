# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from google.appengine.ext import ndb
from babel._compat import izip
from base import GAETestCase
from gaegraph.business_base import CreateArc
from gaepermission.model import MainUser
from mock import patch
from mommygae import mommy
from pswdless.model import PswdUser, PswdUserEmail, EmailUser
from routes.migration import tasks
from tekton import router


class UserMigrationTests(GAETestCase):
    @patch('routes.migration.taskqueue')
    def test_success(self, taskqueue, users_len=3):
        pswd_users_emails = [mommy.save_one(PswdUserEmail, email='a%s@foo.com' % i) for i in range(users_len)]
        pswd_users = [mommy.save_one(PswdUser) for i in range(users_len)]
        keys = [us.key for us in pswd_users]
        for e, u in izip(pswd_users_emails, pswd_users):
            CreateArc(EmailUser, e, u)()

        def task_add_mock(url):
            cursor = router.to_handler(url)[1][0]
            tasks(cursor)

        taskqueue.add = task_add_mock
        tasks()

        self.assertIsNone(PswdUser.query().get())

        main_users = ndb.get_multi(keys)

        for user, pswd_user_email, pswd_user in izip(main_users, pswd_users_emails, pswd_users):
            self.assertIsInstance(user, MainUser)
            self.assertEqual(pswd_user_email.email, user.email)
            self.assertEqual(pswd_user_email.email, user.name)
            self.assertEqual(pswd_user.creation, user.creation)
            self.assertListEqual([''], user.groups)
