# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from mock import Mock
from pswdless import languages
from pswdless.login import SetupLoginTask, SendLoginEmail
from pswdless.sites import InitialSetup, FindCurrentSite

languages.i18n = Mock()


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

def send_login_email(login_id,callback):
    return SendLoginEmail(login_id,callback)

