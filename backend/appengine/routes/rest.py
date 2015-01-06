# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import json
import logging

from gaebusiness.business import CommandExecutionException
from gaecookie.decorator import no_csrf
from gaepermission.decorator import login_required, login_not_required
from pswdless import facade
from tekton.gae.middleware.json_middleware import JsonResponse


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


@login_not_required
@no_csrf
def login(_resp, **kwargs):
    errors = _check_params(('app_id', 'token', 'hook'), ('user_id', 'email', 'lang'), kwargs.keys())
    if not errors:
        cmd = facade.setup_login_task(**kwargs)
        try:
            ticket = cmd()
            return JsonResponse(ticket.key.id())
        except CommandExecutionException:
            errors = cmd.errors

    _resp.status_code = 400
    logging.error(errors)
    return JsonResponse(errors)


@login_not_required
@no_csrf
def detail(_resp, **kwargs):
    errors = _check_params(('app_id', 'token', 'ticket'), (), kwargs.keys())
    if not errors:
        cmd = facade.user_detail(**kwargs)

        try:
            user = cmd()
            return JsonResponse({'id': str(user.key.id()), 'email': user.email})
        except CommandExecutionException:
            errors = cmd.errors

    _resp.status_code = 400
    return JsonResponse(errors)


@login_required
def save_site(_logged_user, _resp, **kwargs):
    errors = _check_params(('domain',), (), kwargs.keys())
    if not errors:

        cmd = facade.save_site(_logged_user, **kwargs)
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


@login_required
def get_sites(_logged_user, _resp, **kwargs):
    errors = _check_params((), (), kwargs.keys())
    if not errors:
        cmd = facade.get_sites(_logged_user, **kwargs)
        try:
            cmd.execute()

            def extract_site_dct(site):
                site_dct = site.to_dict(include=('domain', 'token'))
                site_dct['id'] = str(site.key.id())
                return site_dct

            sites_dct = [extract_site_dct(site) for site in cmd.result]

            return JsonResponse(sites_dct)
        except CommandExecutionException:
            errors = cmd.errors
    _resp.status_code = 400
    return JsonResponse({'errors': errors})


@login_required
def update_site(_logged_user, _resp, **kwargs):
    errors = _check_params(('id', 'domain'), (), kwargs.keys())
    if not errors:
        cmd = facade.update_site(_logged_user, kwargs['id'], kwargs['domain'])
        try:
            site = cmd()
            return JsonResponse({'domain': site.domain})
        except CommandExecutionException:
            errors = cmd.errors
    _resp.status_code = 400
    return JsonResponse({'errors': errors})


@login_required
def refresh_site_token(_logged_user, _resp, **kwargs):
    errors = _check_params(('id',), (), kwargs.keys())
    if not errors:
        cmd = facade.refresh_site_token(_logged_user, kwargs['id'])
        try:
            result = cmd()
            return JsonResponse({'token': result.token})
        except CommandExecutionException:
            errors = cmd.errors
    _resp.status_code = 400
    return JsonResponse({'errors': errors})


