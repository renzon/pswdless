# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from base import GAETestCase
from mommygae import mommy
from pswdless import email
from pswdless.email import CertifySiteCredentials

# mocking i18n
from pswdless.model import Site

email._ = lambda s: s


class CertifyCredentialsTests(GAETestCase):
    def test_id_not_existent(self):
        cmd = CertifySiteCredentials('1', 'foo', r'http://www.pswdless.appspot.com/foo?b=2&p=5')
        cmd.execute()
        self.assertIsNone(cmd.result)
        self.assertDictEqual({'site': 'Wrong site id or token'}, cmd.errors)

    def test_id_wrong_token(self):
        site = mommy.make_one(Site, domain='www.pswdless.appspot.com')
        site.put()
        cmd = CertifySiteCredentials(str(site.key.id()), site.token + "foo",
                                     r'http://www.pswdless.appspot.com/foo?b=2&p=5')
        cmd.execute()
        self.assertIsNone(cmd.result)
        self.assertDictEqual({'site': 'Wrong site id or token'}, cmd.errors)

    def _buildCertifyCredentials(self, site, hook=r'http://www.pswdless.appspot.com/foo?b=2&p=5'):
        return CertifySiteCredentials(str(site.key.id()), site.token, hook)

    def _assert_hook_error(self, hook, error_dct):
        site = mommy.make_one(Site, domain='www.pswdless.appspot.com')
        site.put()
        cmd = self._buildCertifyCredentials(site, hook) # ends with co instead of com
        cmd.execute()
        self.assertIsNone(cmd.result)
        self.assertDictEqual(error_dct, cmd.errors)

    def test_wrong_domain(self):
        self._assert_hook_error(r'https://www.pswdless.appspot.co', {'domain': "Invalid domain: www.pswdless.appspot.co"})

    def test_wrong_protocol(self):
        self._assert_hook_error(r'htt://www.pswdless.appspot.com', {'protocol': 'Only http or https allowed, not htt'})
