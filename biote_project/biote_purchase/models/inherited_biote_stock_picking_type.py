import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class BioteStockPickingType(models.Model):
    _inherit = 'biote.stock.picking.type'
    
    code = fields.Selection(selection_add=[('raw_incoming', '原材料采购入库')])
    