# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from urlparse import urlparse

from webapp2_extras.i18n import gettext as _

from gaebusiness.business import CommandList, Command
from gaegraph.business_base import NodeSearch


class CertifySiteToken(Command):
    def __init__(self, site_token, node_search):
        super(CertifySiteToken, self).__init__()
        self.node_search = node_search
        self._site_token = site_token


    def do_business(self, stop_on_error=True):
        site = self.node_search.result
        if site is None or site.token != self._site_token:
            self.add_error('site', _('Wrong site id or token'))
            return self.errors


class CertifySiteHook(Command):
    def __init__(self, hook, node_search):
        super(CertifySiteHook, self).__init__()
        self.node_search = node_search
        self._hook = hook


    def do_business(self, stop_on_error=True):
        parsed_info = urlparse(self._hook)
        site = self.node_search.result
        self._validate_protocol(parsed_info.scheme)
        self._validate_domain(site.domain, parsed_info.netloc)
        return self.errors

    def _validate_domain(self, domain, netloc):
        hook_domain = netloc.split(':')[0] # eliminating the port from de netloc
        if not hook_domain.endswith(domain) and not self.errors:
            self.add_error('domain', _('Invalid domain: %(domain)s') % {'domain': hook_domain})

    def _validate_protocol(self, scheme):
        if not (scheme in ('http', 'https', '')) and not self.errors:
            self.add_error('protocol', _('Only http or https allowed, not %(protocol)s') % {'protocol': scheme})


class CertifySiteCredentials(CommandList):
    def __init__(self, site_id, site_token, hook):
        node_search = NodeSearch(site_id)
        certify_token = CertifySiteToken(site_token, node_search)
        certify_hook = CertifySiteHook(hook, node_search)
        super(CertifySiteCredentials, self).__init__([node_search, certify_token, certify_hook])


    def execute(self, stop_on_error=True):
        return super(CertifySiteCredentials, self).execute(stop_on_error)


class SetupLoginEmailQueue(CommandList):
    def __init__(self, site_id, site_token, hook, user_id=None, user_email=None, lang='en_US'):
        pass


