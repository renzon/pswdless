# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from base import GAETestCase
from gaegraph.business_base import NeighborsSearch
from pswdless.model import PswdUserEmail, EmailUser
from pswdless.users import FindOrCreateUser
from pswdless import users

# mocking i18n
users._ = lambda s: s


class FindOrCreateUserTests(GAETestCase):
    def test_success(self):
        #creating user
        user_email = 'foo@bar.com'
        find_user = FindOrCreateUser(user_email)
        find_user.execute()
        pswd_email = PswdUserEmail.find_by_email(user_email).get()
        self.assertIsNotNone(pswd_email)
        neighbor_search = NeighborsSearch(EmailUser, pswd_email)
        neighbor_search.execute()
        self.assertEqual(1, len(neighbor_search.result),
                         'should be created one, and only one arc linking email with user')
        user = neighbor_search.result[0]
        self.assertEqual(user.key, find_user.result.key)

        #finding same user

        find_user2 = FindOrCreateUser(user_email)
        find_user2.execute()
        possible_duplicated = PswdUserEmail.find_by_email(user_email).fetch()
        self.assertEqual(1, len(possible_duplicated))
        pswd_email2 = possible_duplicated[0]
        self.assertEqual(pswd_email.key, pswd_email2.key)
        neighbor_search = NeighborsSearch(EmailUser, pswd_email)
        neighbor_search.execute()
        self.assertEqual(1, len(neighbor_search.result),
                         'should be created one, and only one,arc linking email with user')
        user2 = neighbor_search.result[0]
        self.assertEqual(user2.key, find_user2.result.key)
        self.assertEqual(user.key, user2.key)

    def test_invalid_email(self):

        def assertErrorMessage(email, error_msg):
            find_user = FindOrCreateUser(email)
            find_user.execute()
            self.assertIsNone(find_user.result)
            self.assertDictEqual({'email': error_msg}, find_user.errors)

        assertErrorMessage('', 'Email is required')
        assertErrorMessage('a', 'Email is invalid')
        assertErrorMessage('a@', 'Email is invalid')
        assertErrorMessage('a@foo', 'Email is invalid')


