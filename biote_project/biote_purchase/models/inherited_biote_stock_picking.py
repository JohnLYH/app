import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class BioteStockPicking(models.Model):
    _inherit = 'biote.stock.picking'

    recevie_id = fields.Many2one(comodel_name='biote.purchase.recevie', string='收货四联单')
    