# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from base import GAETestCase
from gaebusiness.business import CommandExecutionException
from gaegraph.business_base import DestinationsSearch
from gaepermission import facade
from gaepermission.model import MainUser
from mommygae import mommy
from pswdless.users import FindOrCreateUser, FindUserById, FindUserByIdOrEmail
from pswdless import users

# mocking i18n
users._ = lambda s: s


class FindOrCreateUserTests(GAETestCase):
    def test_valid_email(self, cmd_cls=FindOrCreateUser):
        # creating user
        user_email = 'foo@bar.com'
        find_user = cmd_cls(email=user_email)
        find_user.execute()
        users = facade.find_users_by_email_starting_with()()
        self.assertEqual(1, len(users))
        us = users[0]
        self.assertEqual('foo@bar.com', us.email)
        self.assertEqual('foo@bar.com', us.name)
        # finding same user

        find_user2 = cmd_cls(email=user_email)
        find_user2.execute()
        users = facade.find_users_by_email_starting_with()()
        self.assertEqual(1, len(users))
        us = users[0]
        self.assertEqual('foo@bar.com', us.email)
        self.assertEqual('foo@bar.com', us.name)

    def test_invalid_email(self, cmd_cls=FindOrCreateUser, key='email'):
        def assertErrorMessage(email, key):
            find_user = cmd_cls(email=email)
            self.assertRaises(CommandExecutionException, find_user.execute)
            self.assertIsNone(find_user.result)
            self.assertIn(key, find_user.errors)

        assertErrorMessage('', key)
        assertErrorMessage('a', 'email')
        assertErrorMessage('a@', 'email')
        assertErrorMessage('a@foo', 'email')


class FindUserByIdTests(GAETestCase):
    def test_user_not_found(self, cmd_cls=FindUserById):
        cmd = cmd_cls('1')
        self.assertRaises(CommandExecutionException, cmd.execute)
        self.assertDictEqual({'user': 'User not found'}, cmd.errors)

    def test_user_found(self, cmd_cls=FindUserById):
        user = mommy.make_one(MainUser)
        user.put()
        cmd = cmd_cls(str(user.key.id()))
        cmd.execute()
        self.assertDictEqual({}, cmd.errors)
        self.assertEqual(user.key, cmd.result.key)


class FindUserByIdOrEmailTests(FindOrCreateUserTests, FindUserByIdTests):
    def test_user_not_found(self):
        FindUserByIdTests.test_user_not_found(self, FindUserByIdOrEmail)

    def test_user_found(self):
        FindUserByIdTests.test_user_found(self, FindUserByIdOrEmail)

    def test_valid_email(self, cmd_cls=FindOrCreateUser):
        FindOrCreateUserTests.test_valid_email(self, FindUserByIdOrEmail)

    def test_invalid_email(self, cmd_cls=FindOrCreateUser):
        FindOrCreateUserTests.test_invalid_email(self, FindUserByIdOrEmail, 'params')
