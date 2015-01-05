# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from base import GAETestCase
from gaebusiness.business import CommandExecutionException
from gaegraph.business_base import DestinationsSearch
from mommygae import mommy
from pswdless.model import PswdUserEmail, EmailUser, PswdUser
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
        pswd_email = PswdUserEmail.find_by_email(user_email).get()
        self.assertIsNotNone(pswd_email)
        neighbor_search = DestinationsSearch(EmailUser, pswd_email)
        neighbor_search.execute()
        self.assertEqual(1, len(neighbor_search.result),
                         'should be created one, and only one arc linking email with user')
        user = neighbor_search.result[0]
        self.assertEqual(user.key, find_user.result.key)

        # finding same user

        find_user2 = cmd_cls(email=user_email)
        find_user2.execute()
        possible_duplicated = PswdUserEmail.find_by_email(user_email).fetch()
        self.assertEqual(1, len(possible_duplicated))
        pswd_email2 = possible_duplicated[0]
        self.assertEqual(pswd_email.key, pswd_email2.key)
        neighbor_search = DestinationsSearch(EmailUser, pswd_email)
        neighbor_search.execute()
        self.assertEqual(1, len(neighbor_search.result),
                         'should be created one, and only one,arc linking email with user')
        user2 = neighbor_search.result[0]
        self.assertEqual(user2.key, find_user2.result.key)
        self.assertEqual(user.key, user2.key)

    def test_invalid_email(self, cmd_cls=FindOrCreateUser, empty_error={'email': 'Email is required'}):
        def assertErrorMessage(email, error_dct):
            find_user = cmd_cls(email=email)
            self.assertRaises(CommandExecutionException, find_user.execute)
            self.assertIsNone(find_user.result)
            self.assertDictEqual(error_dct, find_user.errors)

        assertErrorMessage('', empty_error)
        assertErrorMessage('a', {'email': 'Email is invalid'})
        assertErrorMessage('a@', {'email': 'Email is invalid'})
        assertErrorMessage('a@foo', {'email': 'Email is invalid'})


class FindUserByIdTests(GAETestCase):
    def test_user_not_found(self, cmd_cls=FindUserById):
        cmd = cmd_cls('1')
        self.assertRaises(CommandExecutionException, cmd.execute)
        self.assertDictEqual({'user': 'User not found'}, cmd.errors)

    def test_user_found(self, cmd_cls=FindUserById):
        user = mommy.make_one(PswdUser)
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
        FindOrCreateUserTests.test_invalid_email(self, FindUserByIdOrEmail,
                                                 {'params': 'One of user id or email must be present'})




