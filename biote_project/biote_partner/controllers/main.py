import logging

from odoo import http
from odoo.http import request, content_disposition
from odoo.modules import get_resource_path

_logger = logging.getLogger(__name__)


class ControllerCustomer(http.Controller):

    @http.route('/customer/export_tmpl', type='http', auth='user')
    def customer_export_tmpl(self, token):
        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/octet-stream; charset=binary'),
                (
                    'Content-Disposition',
                    content_disposition('客户导入模板.xls'))],
            cookies={'fileToken': token})

        tmpl_path = get_resource_path('biote_partner', 'static', 'src', 'file', '客户导入模板.xls')
        with open(tmpl_path, 'rb') as f:
            response.stream.write(f.read())
        return response

    @http.route('/supplier/export_tmpl', type='http', auth='user')
    def supplier_export_tmpl(self, token):
        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/octet-stream; charset=binary'),
                (
                    'Content-Disposition',
                    content_disposition('供应商导入模板.xls'))],
            cookies={'fileToken': token})

        tmpl_path = get_resource_path('biote_partner', 'static', 'src', 'file', '供应商导入模板.xls')
        with open(tmpl_path, 'rb') as f:
            response.stream.write(f.read())
        return response
