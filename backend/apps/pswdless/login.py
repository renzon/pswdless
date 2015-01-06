# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from datetime import datetime, timedelta
import logging
import urllib
from urlparse import urlparse

from google.appengine.ext import ndb
from webapp2_extras.i18n import gettext as _

from gaebusiness.business import Command, to_model_list, CommandParallel, CommandExecutionException
from gaebusiness.gaeutil import TaskQueueCommand
from gaecookie import facade
from gaegraph.business_base import NodeSearch, DestinationsSearch, OriginsSearch, SingleDestinationSearch, \
    CreateSingleOriginArc
from gaegraph.model import to_node_key, Arc
from pswdless.languages import setup_locale
from pswdless.model import Login, LOGIN_CALL, LoginStatus, LoginStatusArc, LoginUser, LoginSite, LOGIN_EMAIL, SiteUser, \
    LOGIN_CLICK, LOGIN_DETAIL
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
        if site is None:
            self.add_error('site', _('Wrong site id or token'))
        else:
            self._validate_protocol(parsed_info.scheme)
            self._validate_domain(site.domain, parsed_info.netloc)

    def _hook_domain(self, netloc):
        hook_domain = netloc.split(':')[0]  # eliminating the port from de netloc
        return hook_domain

    def _validate_domain(self, domain, netloc):
        hook_domain = self._hook_domain(netloc)
        domain = self._hook_domain(domain)
        if not hook_domain.endswith(domain) and not self.errors:
            self.add_error('domain', _('Invalid domain: %(domain)s') % {'domain': hook_domain})

    def _validate_protocol(self, scheme):
        if not (scheme in ('http', 'https')) and not self.errors:
            self.add_error('protocol', _('Only http or https allowed, not %(protocol)s') % {'protocol': scheme})


class CertifySiteCredentials(CommandParallel):
    def __init__(self, site_id, site_token, hook):
        node_search = NodeSearch(site_id)
        certify_token = CertifySiteToken(site_token, node_search)
        certify_hook = CertifySiteHook(hook, node_search)
        super(CertifySiteCredentials, self).__init__(node_search, certify_token, certify_hook)
        self.site_search = node_search

    def do_business(self):
        super(CertifySiteCredentials, self).do_business()
        if not self.errors:
            self.result = self.site_search.result
        return self.errors

    def execute(self, stop_on_error=True):
        return super(CertifySiteCredentials, self).execute()


class AntiSpanSearch(FindUserByIdOrEmail):
    def do_business(self):
        super(AntiSpanSearch, self).do_business()
        if self.result:
            arc = LoginUser.find_last(self.result).get()
            if arc:
                search = NodeSearch(arc.origin.id())
                search.execute()
                lg = search.result

                def is_spam(login):
                    elapsed = datetime.now() - lg.creation
                    return lg.status in (LOGIN_CALL, LOGIN_EMAIL) and elapsed < timedelta(hours=1)

                    # if is_spam(lg):
                    # self.add_error('spam', _('Spam not allowed'))


class ValidateLoginCall(CommandParallel):
    def __init__(self, site_id, site_token, hook, user_id=None, user_email=None):
        user_search = AntiSpanSearch(user_id, user_email)
        certify_site = CertifySiteCredentials(site_id, site_token, hook)
        self.user_search = user_search
        self.site_search = certify_site
        self.user = None
        self.site = None
        super(ValidateLoginCall, self).__init__(user_search, certify_site)

    def do_business(self):
        super(ValidateLoginCall, self).do_business()
        if not self.errors:
            self.user = self.user_search.result
            self.site = self.site_search.result
        return self.errors

    def execute(self):
        return super(ValidateLoginCall, self).execute()


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


class SetupLoginTask(CommandParallel):
    def __init__(self, site_id, site_token, hook, user_id=None, user_email=None, lang='en_US'):
        setup_locale(lang)
        self.lang = lang
        self.validate_login = ValidateLoginCall(site_id, site_token, hook, user_id, user_email)
        self.hook = hook
        super(SetupLoginTask, self).__init__(self.validate_login)


    def do_business(self):
        super(SetupLoginTask, self).do_business()
        logging.info('SetupLoginTask do_business')
        if not self.errors:
            self.create_login = CreateLogin(self.validate_login.user, self.validate_login.site, self.hook)
            self.create_login.set_up()
            self.create_login.do_business()
            login = self.create_login.result
            params = {'login_id': str(login.key.id()), 'lang': self.lang}
            logging.info('SetupLoginTask do_business %r' % params)
            self.task = TaskQueueCommand(settings.TASK_HERO, '/task/send_login_email',
                                         params=params, countdown=4)
            self.task.set_up()
            self.task.do_business()
            self.result = login

    def commit(self):
        if not self.errors:
            return to_model_list(self.create_login.commit()) + to_model_list(self.task.commit())


class ChangeLoginStatus(NodeSearch):
    def __init__(self, login_id, status):
        super(ChangeLoginStatus, self).__init__(login_id)
        self.status = status

    def do_business(self):
        super(ChangeLoginStatus, self).do_business()
        self.result.status = self.status
        login_status = LoginStatus(label=self.status)
        self.login_status = login_status
        self.login_status_future = login_status._put_async()

    def commit(self):
        self.login_status_future.get_result()
        return [self.result, LoginStatusArc(origin=self.result.key, destination=self.login_status.key)]


class SaveSiteUser(CreateSingleOriginArc):
    def __init__(self, site, user):
        super(SaveSiteUser, self).__init__(SiteUser, site, user)


class SendLoginEmail(CommandParallel):
    def __init__(self, login_id, callback):
        self.callback = callback
        self.site_search = SingleDestinationSearch(LoginSite, login_id)
        self.user_search = SingleDestinationSearch(LoginUser, login_id)
        self.change_login = ChangeLoginStatus(login_id, LOGIN_EMAIL)
        super(SendLoginEmail, self).__init__(self.change_login, self.site_search, self.user_search)


    def do_business(self):
        super(SendLoginEmail, self).do_business()
        user = self.user_search.result
        site = self.site_search.result
        self.callback(self.change_login.result, site, user)
        if not self.errors:
            try:
                SaveSiteUser(site, user).execute()
            except CommandExecutionException:
                pass


class ValidateLoginStatus(NodeSearch):
    def __init__(self, login_id, valid_status, new_status):
        super(ValidateLoginStatus, self).__init__(login_id)
        self.new_status = new_status
        self.valid_status = valid_status

    def do_business(self):
        super(ValidateLoginStatus, self).do_business()
        if self.result is None or self.result.status != self.valid_status:
            self.add_error('ticket', _('Invalid Call'))
            return self.errors
        self.result.status = self.new_status
        login_status = LoginStatus(label=self.new_status)
        self.login_status = login_status
        self.login_status_future = login_status._put_async()

    def commit(self):
        if not self.errors:
            self.login_status_future.get_result()
            return [self.result, LoginStatusArc(origin=self.result.key, destination=self.login_status.key)]


class ValidateLoginLink(CommandParallel):
    def __init__(self, signed_ticket_id, redirect):
        self.redirect = redirect
        cmd = facade.retrieve('ticket', signed_ticket_id, settings.LINK_EXPIRATION)
        logging.error(settings.LINK_EXPIRATION)
        cmd.execute()
        if cmd.result is None:
            super(ValidateLoginLink, self).__init__()
            self.validate_status = None
            self.add_error('ticket', _('Invalid Call'))
        else:
            self.validate_status = ValidateLoginStatus(cmd.result, LOGIN_EMAIL, LOGIN_CLICK)
            super(ValidateLoginLink, self).__init__(self.validate_status)


    def do_business(self):
        super(ValidateLoginLink, self).do_business()
        self.result = self.validate_status.result if self.validate_status else None
        login = self.result
        if login and not self.errors and self.redirect:
            hook = login.hook
            query = urllib.urlencode({'ticket': str(login.key.id())})
            if hook.find('?') >= 0:
                self.redirect(str(hook + '&' + query))
            else:

                self.redirect(str(hook + '?' + query))

    def execute(self):
        super(ValidateLoginLink, self).execute()


class LogUserIn(DestinationsSearch):
    def __init__(self, ticket_id, response, url_detail, **kwargs):
        super(LogUserIn, self).__init__(LoginSite, ticket_id, ticket_id=ticket_id, response=response,
                                        url_detail=url_detail, **kwargs)

    def do_business(self, stop_on_error=False):
        super(LogUserIn, self).do_business(stop_on_error)
        site = self.result[0]
        if site and not self.errors:
            log_user_in = facade.log_user_in(site.key.id(), site.token, self.ticket_id, self.response,
                                             url_detail=self.url_detail)
            log_user_in.execute()
            self.errors = log_user_in.errors



