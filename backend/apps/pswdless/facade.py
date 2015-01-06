# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from pswdless.login import SetupLoginTask, SendLoginEmail, ValidateLoginLink, LogUserIn, UserDetail
from pswdless.sites import InitialSetup, FindCurrentSite, SaveSite, FindUserSites, UpdateSite


def initial_setup():
    '''
    Creates the first user as the owner of the first Client Site, that is the host
    It is restricted to Google App Engine admins and works only the first time it is executed
    '''
    return InitialSetup()


def setup_login_task(app_id, token, hook, user_id=None, email=None, lang='en_US'):
    return SetupLoginTask(app_id, token, hook, user_id, email, lang)


def find_current_site():
    return FindCurrentSite()


def send_login_email(login_id, callback):
    return SendLoginEmail(login_id, callback)


def validate_login_link(signed_ticket_id, redirect):
    return ValidateLoginLink(signed_ticket_id, redirect)


def log_user_in(ticket_id, response, url_detail):
    return LogUserIn(ticket_id, response, url_detail)


def save_site(user, domain):
    return SaveSite(user, domain)


def get_sites(user):
    return FindUserSites(user)


def update_site(user_id, site_id, new_domain):
    return UpdateSite(user_id, site_id, new_domain)


def refresh_site_token(user_id, site_id):
    return UpdateSite(user_id, site_id, token=True)


def user_detail(app_id, token, ticket):
    return UserDetail(app_id, token, ticket)