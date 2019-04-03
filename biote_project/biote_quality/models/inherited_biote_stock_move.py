import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class BioteStockMove(models.Model):
    _inherit = 'biote.stock.move'

    allow_id = fields.Many2one(comodel_name='biote.allow', string='放行单号')
    unqualified_id = fields.Many2one(comodel_name='biote.unqualified', string='不合格处置单')
