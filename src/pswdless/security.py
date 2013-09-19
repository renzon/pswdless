# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import functools
import inspect
from os import urandom
from pswdclient import facade
import settings


def extract_xsrf_token(request):
    token = request.cookies.get(settings.XSRF_TOKEN)
    if token:
        cmd = facade.retrieve_dct(settings.XSRF_TOKEN, token, settings.XSRF_TOKEN_EXPIRATION)
        cmd.execute()
        return cmd.result


def generate_xsrf_token():
    random = urandom(16).encode('hex')
    cmd = facade.sign_dct(settings.XSRF_TOKEN, random)
    cmd.execute()
    return cmd.result, random

def current_user_and_email(request):
    cmd=facade.logged_user(request)
    cmd.execute()
    return cmd.result


def xsrf(fcn):
    def wrapper(_dependencies, _req, _resp, xsrf_token=None, **kwargs):
        if _req.method in ('POST', 'PUT', 'DELETE'):
            token = xsrf_token or _req.cookies.get(settings.XSRF_ANGULAR_AJAX_COOKIE)
            if token:
                signed_token = extract_xsrf_token(_req)
                if token == signed_token:
                    fcn_args = inspect.getargspec(fcn)[0]
                    _fcn_dependencies = {k: _dependencies[k] for k in fcn_args if k in _dependencies}
                    kwargs.update(_fcn_dependencies)
                    return fcn(**kwargs)
        _resp.status_code = 403
        raise Exception('XSRF Problem')

    return functools.update_wrapper(wrapper, fcn)





