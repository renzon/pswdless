# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import json
from pswdless import facade
from pswdless.security import logged_ajax, xsrf, current_user_and_email


def _check_params(mandatory_params, optional_params, current_params):
    mandatory_set = frozenset(mandatory_params)
    current_params = frozenset(current_params)
    if not mandatory_set.issubset(current_params):
        missing_params = mandatory_set.difference(current_params)
        missing_params = ', '.join(missing_params)
        return {'errors': {'params': 'Missing param(s): %s' % missing_params}}

    all_params_set = frozenset(optional_params + mandatory_params)
    if not all_params_set.issuperset(current_params):
        unexpected_params = current_params.difference(all_params_set)
        unexpected_params = ', '.join(unexpected_params)
        return {'errors': {'params': 'Unexpected param(s): %s' % unexpected_params}}


def login(_resp, **kwargs):
    errors = _check_params(('app_id', 'token', 'hook'), ('user_id', 'email', 'lang'), kwargs.keys())
    if not errors:
        cmd = facade.setup_login_task(**kwargs)
        cmd.execute()
        if cmd.errors:
            errors = cmd.errors
        else:
            ticket = json.dumps({'ticket': str(cmd.result.key.id())})
            return _resp.write(ticket)

    _resp.status_code = 400
    return _resp.write(json.dumps({'errors': errors}))


def detail(_resp, **kwargs):
    errors = _check_params(('app_id', 'token', 'ticket'), (), kwargs.keys())
    if not errors:
        cmd = facade.user_detail(**kwargs)
        cmd.execute()
        if cmd.errors:
            errors = cmd.errors
        else:
            user = json.dumps({'id': str(cmd.result[0].key.id()), 'email': cmd.email})
            return _resp.write(user)

    _resp.status_code = 400
    return _resp.write(json.dumps({'errors': errors}))


@logged_ajax
@xsrf
def save_site(_req, _resp, **kwargs):
    errors = _check_params(('domain',), (), kwargs.keys())
    if not errors:
        user_detail = current_user_and_email(_req)
        cmd = facade.save_site(user_detail['id'], **kwargs)
        cmd.execute()
        if cmd.errors:
            errors = cmd.errors
        else:
            site = cmd.result
            site_dct = site.to_dict(include=('domain', 'token'))
            site_dct['id'] = str(site.key.id())
            return _resp.write(json.dumps(site_dct))

    _resp.status_code = 400
    return _resp.write(json.dumps({'errors': errors}))


@logged_ajax
@xsrf
def get_sites(_req, _resp, **kwargs):
    errors = _check_params((), (), kwargs.keys())
    if not errors:
        user_detail = current_user_and_email(_req)
        cmd = facade.get_sites(user_detail['id'], **kwargs)
        cmd.execute()
        if cmd.errors:
            errors = cmd.errors
        else:

            def extract_site_dct(site):
                site_dct = site.to_dict(include=('domain', 'token'))
                site_dct['id'] = str(site.key.id())
                return site_dct

            sites_dct = [extract_site_dct(site) for site in cmd.result]

            return _resp.write(json.dumps(sites_dct))

    _resp.status_code = 400
    return _resp.write(json.dumps({'errors': errors}))


@logged_ajax
@xsrf
def update_site(_req, _resp, **kwargs):
    errors = _check_params(('id', 'domain'), (), kwargs.keys())
    if not errors:
        user_detail = current_user_and_email(_req)
        cmd = facade.update_site(user_detail['id'], kwargs['id'],kwargs['domain'])
        cmd.execute()
        if cmd.errors:
            errors = cmd.errors
        else:
            return _resp.write(cmd.result.domain)
    _resp.status_code = 400
    return _resp.write(json.dumps({'errors': errors}))

@logged_ajax
@xsrf
def refresh_site_token(_req, _resp, **kwargs):
    errors = _check_params(('id',), (), kwargs.keys())
    if not errors:
        user_detail = current_user_and_email(_req)
        cmd = facade.refresh_site_token(user_detail['id'], kwargs['id'])
        cmd.execute()
        if cmd.errors:
            errors = cmd.errors
        else:
            return _resp.write(cmd.result.token)
    _resp.status_code = 400
    return _resp.write(json.dumps({'errors': errors}))


