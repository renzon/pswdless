import jinja2
from webapp2_extras import i18n
import os

_base = os.path.dirname(__file__)
_base = os.path.join(_base, "web")
_jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader([_base]),
    trim_blocks=True,
    autoescape=True,
    extensions=['jinja2.ext.i18n'])

_jinja_environment.install_gettext_translations(i18n)


def render(template_name, values={}):
    template = _jinja_environment.get_template(template_name)
    return template.render(values)

