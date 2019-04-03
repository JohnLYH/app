import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class CustomerOperationWizard(models.TransientModel):
    _name = 'customer.operation.wizard'

    import_excel = fields.Binary(string='导入数据')
