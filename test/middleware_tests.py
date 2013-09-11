# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import unittest
from base import GAETestCase
import middlewares
from mock import Mock
from pswdless.security import generate_xsrf_token
import settings


class SetupLanguageTest(unittest.TestCase):
    def test_language_on_cookie(self):
        # Mocking
        next_process = Mock()
        request = Mock()
        i18n_locale = Mock()
        i18n_locale.set_locale = Mock()
        middlewares.i18n.get_i18n = lambda: i18n_locale
        request.cookies.get = Mock(return_value="pt_BR")
        # Test
        middlewares.setup_language(request, None, next_process)

        # Assertions
        next_process.assert_called_once_with()
        i18n_locale.set_locale.assert_called_once_with("pt_BR")


    def test_language_from_header(self):
        # Mocking
        next_process = Mock()
        request = Mock()
        i18n_locale = Mock()
        i18n_locale.set_locale = Mock()
        middlewares.i18n.get_i18n = lambda: i18n_locale
        request.cookies.get = Mock(return_value=None)
        request.headers.get = Mock(return_value="pt-BR, en-US")
        response = Mock()
        response.set_cookie = Mock()

        # Test
        middlewares.setup_language(request, response, next_process)

        # Assertions
        next_process.assert_called_once_with()
        i18n_locale.set_locale.assert_called_once_with("pt_BR")
        response.set_cookie.assert_called_once_with(settings.LANG_COOKIE, "pt_BR")

    def test_language_from_header_not_in_available_languages(self):
        # Mocking
        next_process = Mock()
        request = Mock()
        i18n_locale = Mock()
        i18n_locale.set_locale = Mock()
        middlewares.i18n.get_i18n = lambda: i18n_locale
        request.cookies.get = Mock(return_value=None)
        request.headers.get = Mock(return_value="not available language")
        response = Mock()
        response.set_cookie = Mock()

        # Test
        middlewares.setup_language(request, response, next_process)

        # Assertions
        next_process.assert_called_once_with()
        i18n_locale.set_locale.assert_called_once_with(settings.DEFAULT_LOCALE)
        response.set_cookie.assert_called_once_with(settings.LANG_COOKIE, settings.DEFAULT_LOCALE)


class XSRFCoolieTests(GAETestCase):
    def test_cookie_reuse(self):
        token, random_number = generate_xsrf_token()
        cookies = Mock()
        cookies.get = Mock(return_value=token)
        request = Mock()
        request.cookies = cookies
        resp = Mock()
        generate_xsrf_token_mock = Mock(return_value=(token, random_number))
        middlewares.generate_xsrf_token = generate_xsrf_token_mock
        next_process = Mock()
        middlewares.xsrf_cookie(request, resp, next_process)
        resp.set_cookie.assert_any_call(settings.XSRF_TOKEN, token, httponly=True)
        resp.set_cookie.assert_any_call(settings.XSRF_ANGULAR_COOKIE, random_number, httponly=True)
        self.assertFalse(generate_xsrf_token_mock.called)
        next_process.assert_called_once_with()

    def test_cookie_reuse(self):
        token, random_number = generate_xsrf_token()
        cookies = Mock()
        cookies.get = Mock(return_value=None)
        request = Mock()
        request.cookies = cookies
        resp = Mock()
        generate_xsrf_token_mock = Mock(return_value=(token, random_number))
        middlewares.generate_xsrf_token = generate_xsrf_token_mock
        next_process = Mock()
        middlewares.xsrf_cookie(request, resp, next_process)
        resp.set_cookie.assert_any_call(settings.XSRF_TOKEN, token, httponly=True, overwrite=True)
        resp.set_cookie.assert_any_call(settings.XSRF_ANGULAR_COOKIE, random_number, httponly=True, overwrite=True)
        generate_xsrf_token_mock.assert_called_once_with()
        next_process.assert_called_once_with()




