# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from pswdless.login import SetupLoginTask
from pswdless.sites import InitialSetup


def initial_setup():
    '''
    Creates the first user as the owner of the first Client Site, that is the host
    It is restricted to Google App Engine admins and works only the first time it is executed
    '''
    return InitialSetup()


def setup_login_task(site_id, site_token, hook, user_id=None, user_email=None, lang='en_US'):
    return SetupLoginTask(site_id, site_token, hook, user_id, user_email, lang)
