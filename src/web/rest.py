# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import json
import logging
from pswdless import facade


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
            logging.critical(ticket)
            return _resp.write(ticket)

    _resp.status_code = 400
    return _resp.write(json.dumps(errors))

