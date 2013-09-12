# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from pswdless.sites import InitialSetup


def initial_setup():
    '''
    Creates the first user as the owner of the first Client Site, that is the host
    It is restricted to Google App Engine admins and works only the first time it is executed
    '''
    return InitialSetup()


def send_login_email():
    pass
