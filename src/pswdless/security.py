# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import functools
import inspect
import json

from webapp2_extras.i18n import gettext as _

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
    cmd = facade.logged_user(request)
    cmd.execute()
    return cmd.result


def logged(fcn):
    def wrapper(_dependencies, _req, _write_tmpl, xsrf_token=None, **kwargs):
        user_detail = current_user_and_email(_req)
        if user_detail:
            fcn_args = inspect.getargspec(fcn)[0]
            _fcn_dependencies = {k: _dependencies[k] for k in fcn_args if k in _dependencies}
            kwargs.update(_fcn_dependencies)
            return fcn(**kwargs)
        else:
            _write_tmpl("/templates/login_required.html")

    return functools.update_wrapper(wrapper, fcn)


def logged_ajax(fcn):
    def wrapper(_dependencies, _req, _resp, xsrf_token=None, **kwargs):
        user_detail = current_user_and_email(_req)
        if user_detail:
            fcn_args = inspect.getargspec(fcn)[0]
            _fcn_dependencies = {k: _dependencies[k] for k in fcn_args if k in _dependencies}
            kwargs.update(_fcn_dependencies)
            return fcn(**kwargs)
        else:
            _resp.status_code = 400
            errors = {'errors': {'login': _('Must be logged to make this call')}}
            _resp.write(json.dumps(errors))

    return functools.update_wrapper(wrapper, fcn)


def xsrf(fcn):
    def wrapper(_dependencies, _req, _resp, xsrf_token=None, **kwargs):
        ajax_token = _req.headers.get(settings.XSRF_ANGULAR_AJAX_COOKIE)
        if _req.method in ('POST', 'PUT', 'DELETE'):
            token = xsrf_token or ajax_token
            if token:
                signed_token = extract_xsrf_token(_req)
                if token == signed_token:
                    fcn_args = inspect.getargspec(fcn)[0]
                    _fcn_dependencies = {k: _dependencies[k] for k in fcn_args if k in _dependencies}
                    kwargs.update(_fcn_dependencies)
                    return fcn(**kwargs)
        _resp.status_code = 403
        if ajax_token:
            return _resp.write(json.dumps({'errors': _('XSRF Atack!')}))
        raise Exception('XSRF Problem')

    return functools.update_wrapper(wrapper, fcn)





