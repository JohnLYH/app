import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class BioteUnqualifiedDoneWiz(models.Model):
    _name = 'biote.unqualified.done.wiz'
    _description = '不合格处置单完成向导'

    unqualified_id = fields.Many2one(comodel_name='biote.unqualified', string='不合格品处置单')
    handle_id = fields.Many2one(comodel_name='biote.unqualified.handle', string='不合格品处置方式')
    handle_qty = fields.Float(string='处置数量')
    can_handle_qty = fields.Float(string='可处置数量')

    @api.multi
    def action_done(self):
        self.ensure_one()
        if self.handle_qty > self.can_handle_qty:
            raise UserError('处置数量超过最大可处置数量！')
        self.unqualified_id.action_done(self.handle_id, self.handle_qty)