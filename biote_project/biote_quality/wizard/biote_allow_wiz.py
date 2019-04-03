import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class BioteAllowWiz(models.TransientModel):
    _name = 'biote.allow.wiz'
    _description = '放行单向导'

    state = fields.Selection(string='放行状态', selection=[('approve', '放行'), ('refused', '不放行')])
    allow_qty = fields.Float(string='放行数量')
    refused_qty = fields.Float(string='不放行数量')
    max_qty = fields.Float(string='最大处置数量')
    allow_id = fields.Many2one(comodel_name='biote.allow', string='放行单号')
    # allow_record_id = fields.Reference(selection='_reference_models', string='放行单号')

    # @api.model
    # def _reference_models(self): 
    #     return []

    def action_done(self):
        self.ensure_one()
        if self.allow_qty > self.max_qty or self.refused_qty > self.max_qty:
            raise UserError('放行单处置的数量超过单据的最大数量')
        if self.allow_id:
            self.allow_id.action_done(self.state, self.allow_qty, self.refused_qty)
