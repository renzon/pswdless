# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from urlparse import urlparse
from google.appengine.ext import ndb

from webapp2_extras.i18n import gettext as _

from gaebusiness.business import CommandList, Command, to_model_list
from gaebusiness.gaeutil import TaskQueueCommand
from gaegraph.business_base import NodeSearch
from gaegraph.model import to_node_key
from pswdless.languages import setup_locale
from pswdless.model import Login, LOGIN_CALL, LoginStatus, LoginStatusArc, LoginUser, LoginSite
from pswdless.users import FindUserByIdOrEmail
import settings


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
        if not (scheme in ('http', 'https')) and not self.errors:
            self.add_error('protocol', _('Only http or https allowed, not %(protocol)s') % {'protocol': scheme})


class CertifySiteCredentials(CommandList):
    def __init__(self, site_id, site_token, hook):
        node_search = NodeSearch(site_id)
        certify_token = CertifySiteToken(site_token, node_search)
        certify_hook = CertifySiteHook(hook, node_search)
        super(CertifySiteCredentials, self).__init__([node_search, certify_token, certify_hook])
        self.site_search = node_search

    def do_business(self, stop_on_error=True):
        super(CertifySiteCredentials, self).do_business(stop_on_error)
        if not self.errors:
            self.result = self.site_search.result
        return self.errors

    def execute(self, stop_on_error=True):
        return super(CertifySiteCredentials, self).execute(stop_on_error)


class ValidateLoginCall(CommandList):
    def __init__(self, site_id, site_token, hook, user_id=None, user_email=None):
        user_search = FindUserByIdOrEmail(user_id, user_email)
        certify_site = CertifySiteCredentials(site_id, site_token, hook)
        self.user_search = user_search
        self.site_search = certify_site
        self.user = None
        self.site = None
        super(ValidateLoginCall, self).__init__([user_search, certify_site])

    def do_business(self, stop_on_error=True):
        super(ValidateLoginCall, self).do_business(stop_on_error)
        if not self.errors:
            self.user = self.user_search.result
            self.site = self.site_search.result
        return self.errors

    def execute(self, stop_on_error=True):
        return super(ValidateLoginCall, self).execute(stop_on_error)


class CreateLogin(Command):
    def __init__(self, user, site, hook):
        super(CreateLogin, self).__init__()
        self.user = user
        self.site = site
        self.result = Login(hook=hook, status=LOGIN_CALL)
        self.login_status = LoginStatus(label=LOGIN_CALL)

    def set_up(self):
        self._future = ndb.put_multi_async([self.result, self.login_status])

    def do_business(self, stop_on_error=False):
        for f in self._future:
            f.get_result()

    def commit(self):
        return [cls(origin=to_node_key(self.result), destination=to_node_key(obj)) for cls, obj in
                [(LoginStatusArc, self.login_status), (LoginUser, self.user), (LoginSite, self.site)]]


class SetupLoginTask(Command):
    def __init__(self, site_id, site_token, hook, user_id=None, user_email=None, lang='en_US'):
        setup_locale(lang)
        self.validate_login = ValidateLoginCall(site_id, site_token, hook, user_id, user_email)
        self.hook = hook
        super(SetupLoginTask, self).__init__()

    def set_up(self):
        self.validate_login.execute()
        self.errors = self.validate_login.errors

    def do_business(self, stop_on_error=False):
        if not self.errors:
            self.create_login = CreateLogin(self.validate_login.user, self.validate_login.site, self.hook)
            self.create_login.set_up()
            self.create_login.do_business()
            login = self.create_login.result
            self.task = TaskQueueCommand(settings.TASK_HERO, '/task/send_login_email',
                                         params={'login': str(login.key.id())})
            self.task.set_up()
            self.task.do_business()
            self.result = login

    def commit(self):
        if not self.errors:
            return to_model_list(self.create_login.commit()) + to_model_list(self.task.commit())

