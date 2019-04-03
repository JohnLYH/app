import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class ControllerName(http.Controller):

    # <t t-call="website.layout"> 需要使用website=True
    @http.route('', type='http', auth='user')
    def fun(self, data, token):
        pass
