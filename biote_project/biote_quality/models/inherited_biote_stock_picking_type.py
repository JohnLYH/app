import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class BioteStockPickingType(models.Model):
    _inherit = 'biote.stock.picking.type'

    code = fields.Selection(selection_add=[
        ('unqualified_incoming', '不良品入库'),
        ('unqualified_return', '不良品退货'),
        ('unqualified_scrap', '不良品报废')
    ])