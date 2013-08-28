# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import unittest
import middlewares
from mock import Mock
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

