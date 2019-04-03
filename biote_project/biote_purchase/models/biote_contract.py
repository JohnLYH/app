import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class BioteContract(models.Model):
    _inherit = 'biote.contract'

    biote_purchase_plan_id = fields.Many2one(
        comodel_name='biote.purchase.plan', string='关联采购计划')