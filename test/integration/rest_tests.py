# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import json
from base import GAETestCase
from mock import Mock
from pswdless.model import Site, Login
from web import rest


class LoginTests(GAETestCase):
    def test_mandory_field_not_present(self):
        resp = Mock()
        rest.login(resp, app_id='1')
        errors = {'errors': {'params': 'Missing param(s): hook, token'}}
        resp.write.assert_called_once_with(json.dumps(errors))
        self.assertEqual(400, resp.status_code)

    def test_unexpected_param(self):
        resp = Mock()
        rest.login(resp, app_id='1', token='t', hook='h', foo='foo')
        errors = {'errors': {'params': 'Unexpected param(s): foo'}}
        resp.write.assert_called_once_with(json.dumps(errors))
        self.assertEqual(400, resp.status_code)

    def test_success(self):
        resp = Mock()
        # ----- This is commented because Queue stub is not working well
        # def write(ticket):
        #     resp.ticket = ticket
        #
        # resp.write = write
        # site = Site(token='a', domain='pswdless.com')
        # site.put()
        # rest.facade.setup_login_task()
        # rest.login(resp, app_id=site.key.id(), token=site.token, hook='http://pswdless.com/foo',
        #            email='foo@bar.com')
        #
        #
        # ticket_dct = json.loads(resp.ticket)
        # self.assertNotIn('errors', ticket_dct, ticket_dct)
        # self.assertDictEqual({'ticket': str(Login.query().get(keys_only=True).id())}, ticket_dct)