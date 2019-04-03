import logging

from odoo import http
from odoo.http import request, content_disposition
from odoo.modules import get_resource_path


_logger = logging.getLogger(__name__)


class ControllerName(http.Controller):

    @http.route('/export_tmpl', type='http', auth='user')
    def product_export_tmpl(self, token):
        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/octet-stream; charset=binary'),
                (
                    'Content-Disposition',
                    content_disposition('产品导入模板.xls'))],
            cookies={'fileToken': token})

        tmpl_path = get_resource_path('rongbiz_stock', 'static', 'src', 'file', '产品导入模板.xls')
        with open(tmpl_path, 'rb') as f:
            response.stream.write(f.read())
        return response
