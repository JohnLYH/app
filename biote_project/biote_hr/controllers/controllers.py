import logging
from odoo import http
from odoo.http import request
from odoo.http import request, content_disposition
from odoo.modules import get_resource_path

_logger = logging.getLogger(__name__)

file_name = 'hr_employee_tmpl.xls'


class ExcelExport(http.Controller):

    @http.route('/get_biote_hr_employee_template', type='http', auth='user')
    def export_employee_tmpl(self, token):
        response = request.make_response(
            None,
            headers=[('Content-Type', 'application/octet-stream; charset=binary'),
                     ('Content-Disposition', content_disposition(file_name)), ],
            cookies={'fileToken': token})
        tmpl_path = get_resource_path('biote_hr', 'static', 'Excel', file_name)
        with open(tmpl_path, 'rb') as f:
            response.stream.write(f.read())
        return response
