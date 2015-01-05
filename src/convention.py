# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import json
import sys

import os



#Put lib on path, once Google App Engine does not allow doing it directly
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

from pswdless.security import extract_xsrf_token
from webapp2_extras import i18n
import middlewares
import settings
import tmpl
import logging
import traceback
import webapp2
from zen import router
from zen.router import PathNotFound
from pswdless import security


def _extract_values(handler, param, default_value=""):
    values = handler.request.get_all(param)
    if param.endswith("[]"):
        return param[:-2], values if values else []
    else:
        if not values: return param, default_value
        if len(values) == 1: return param, values[0]
        return param, values


def execute_middlewares(midlewares, req, resp, handler_fcn):
    if midlewares:
        current_middleware = midlewares[0]

        def next_process():
            next_middlewares = midlewares[1:]
            execute_middlewares(next_middlewares, req, resp, handler_fcn)

        current_middleware(req, resp, next_process)
    else:
        handler_fcn()


class BaseHandler(webapp2.RequestHandler):
    def get(self):
        self.make_convetion()

    def post(self):
        self.make_convetion()

    def make_convetion(self):
        angular_ajax_accept = r'application/json, text/plain, */*'
        header_value = getattr(self.request, 'accept', None)
        header_value = getattr(header_value, 'header_value', None)
        if header_value == angular_ajax_accept and self.request.body:
            kwargs = json.loads(self.request.body)
        else:
            kwargs = dict(_extract_values(self, a) for a in self.request.arguments())

        def write_tmpl(template_name, values={}):
            values['APP_NAME'] = settings.APP_NAME
            values['APP_HOST'] = settings.APP_HOST
            xsrf_token = extract_xsrf_token(self.request)
            if xsrf_token is None:
                xsrf_token = middlewares.xsrf_cookie(self.request, self.response, lambda: None)
            values['XSRF_TOKEN'] = xsrf_token
            i18n_obj = i18n.get_i18n()
            values['CURRENT_LANGUAGE'] = i18n_obj.locale
            values['current_user'] = security.current_user_and_email(self.request)
            return self.response.write(tmpl.render(template_name, values))

        convention_params = {"_req": self.request,
                             "_resp": self.response,
                             "_handler": self,
                             "_render": tmpl.render,
                             "_write_tmpl": write_tmpl}
        convention_params["_dependencies"] = convention_params
        try:
            fcn, params = router.to_handler(self.request.path, convention_params, **kwargs)

            def handler_fcn():
                fcn(*params, **kwargs)

            execute_middlewares(middlewares.MIDLEWARE_LIST, self.request, self.response, handler_fcn)
        except PathNotFound:
            self.response.status_code = 404
            logging.error("Path not Found: " + self.request.path)
        except:
            self.response.status_code = 400
            logging.error((fcn, params, kwargs))
            logging.error(traceback.format_exc())


app = webapp2.WSGIApplication([("/.*", BaseHandler)], debug=False)

