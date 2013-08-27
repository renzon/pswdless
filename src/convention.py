# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import sys
import os
#Put lib on path, once Google App Engine does not allow doing it directly
import settings

sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

from webapp2_extras import i18n
import tmpl
import logging
import traceback
import webapp2
from zen import router
from zen.router import PathNotFound


def _extract_values(handler, param, default_value=""):
    values = handler.request.get_all(param)
    if param.endswith("[]"):
        return param[:-2], values if values else []
    else:
        if not values: return param, default_value
        if len(values) == 1: return param, values[0]
        return param, values


class BaseHandler(webapp2.RequestHandler):
    def get(self):
        self.make_convetion()

    def post(self):
        self.make_convetion()

    def make_convetion(self):
        kwargs = dict(_extract_values(self, a) for a in self.request.arguments())
        locale = self.request.headers.get("Accept-Language", "en_US").split(",")[0]
        locale = locale.replace("-", "_")
        i18n.get_i18n().set_locale(locale)

        def write_tmpl(template_name, values={}):
            values['APP_NAME']=settings.APP_NAME
            values['APP_HOST']=settings.APP_HOST
            return self.response.write(tmpl.render(template_name, values))

        convention_params = {"_req": self.request,
                             "_resp": self.response,
                             "_handler": self,
                             "_render": tmpl.render,
                             "_write_tmpl": write_tmpl}
        convention_params["_dependencies"] = convention_params
        try:
            fcn, params = router.to_handler(self.request.path, convention_params, **kwargs)
            fcn(*params, **kwargs)
        except PathNotFound:
            logging.error("Path not Found: " + self.request.path)
        except:
            logging.error((fcn, params, kwargs))
            logging.error(traceback.format_exc())


app = webapp2.WSGIApplication([("/.*", BaseHandler)], debug=False)

