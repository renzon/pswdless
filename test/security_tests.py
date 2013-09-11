# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from base import GAETestCase
from mock import Mock
from pswdless.security import generate_xsrf_token, extract_xsrf_token, xsrf
import settings


class XSRFTests(GAETestCase):
    def test_extract_generate_token(self):
        token, random_item = generate_xsrf_token()
        self.assertNotEqual(token, random_item)
        req = Mock()
        req.cookies.get = Mock(return_value=token)
        extracted = extract_xsrf_token(req)
        self.assertEqual(random_item, extracted)

    def test_method_get_exception(self):
        fcn_mock = Mock()

        @xsrf
        def fcn():
            fcn_mock()

        resp = Mock()
        req = Mock()
        req.method = 'GET'
        self.assertRaises(Exception, fcn, {}, req, resp)
        self.assertFalse(fcn_mock.called)
        self.assertEqual(403, resp.status_code)

    def test_method_post_with_no_tokens(self):
        fcn_mock = Mock()

        @xsrf
        def fcn():
            fcn_mock()

        resp = Mock()
        req = Mock()
        req.method = 'POST'
        req.cookies.get = Mock(return_value=None)
        self.assertRaises(Exception, fcn, {}, req, resp)
        self.assertFalse(fcn_mock.called)
        self.assertEqual(403, resp.status_code)

    def test_method_post_with_wrong_token(self):
        fcn_mock = Mock()
        token, random_str = generate_xsrf_token()

        @xsrf
        def fcn():
            fcn_mock()

        resp = Mock()
        req = Mock()
        req.method = 'POST'
        req.cookies.get = Mock(return_value=token)
        wrong_item=random_str[1:]
        self.assertRaises(Exception, fcn, {}, req, resp,wrong_item)
        self.assertFalse(fcn_mock.called)
        self.assertEqual(403, resp.status_code)

    def test_method_post(self):
        fcn_mock = Mock()
        token, random_str = generate_xsrf_token()

        @xsrf
        def fcn():
            fcn_mock()

        resp = Mock()
        req = Mock()
        req.method = 'POST'
        req.cookies.get = Mock(return_value=token)
        fcn({}, req, resp,random_str)
        fcn_mock.assert_called_once_with()

    def test_method_post_from_angular_js_ajax(self):
        fcn_mock = Mock()
        token, random_str = generate_xsrf_token()

        @xsrf
        def fcn():
            fcn_mock()

        resp = Mock()
        req = Mock()
        req.method = 'POST'
        req.cookies.get = lambda k: token if k==settings.XSRF_TOKEN else random_str
        fcn({}, req, resp)
        fcn_mock.assert_called_once_with()

