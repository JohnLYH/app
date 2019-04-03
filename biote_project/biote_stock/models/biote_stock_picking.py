import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class BioteStockPicking(models.Model):
    _name = 'biote.stock.picking'
    _description = '博益特库存调拨单'

    name = fields.Char(string='单号')
    move_ids = fields.One2many(
        comodel_name='biote.stock.move', inverse_name='picking_id', string='入库单明细')
    state = fields.Selection(
        string='入库单状态', 
        selection=[('draft', '草稿'), ('partially', '部分入库'), ('done', '完成')], 
        compute='_compute_picking_state',
        store=True
    )
    picking_type_id = fields.Many2one(comodel_name='biote.stock.picking.type', string='作业类型')
    code = fields.Selection(related='picking_type_id.code', store=True)
    
    @api.depends('move_ids', 'move_ids.state')
    def _compute_picking_state(self):
        for picking in self:
            done_lines = picking.move_ids.filtered(lambda r: r.state == 'done')
            if not (picking.move_ids - done_lines):
                picking.state = 'done'
            else:
                if done_lines:
                    picking.state = 'partially'
                else:
                    picking.state = 'draft'

    @api.multi
    def action_draft_select_dialog(self):
        self.ensure_one()
        draft_line_ids = self.move_ids._get_draft_moves().ids
        action = {
            'type': 'ir.actions.client',
            'tag': 'select_dialog',
            'context': {
                'title': '库存移动',
                'method': 'action_done',
                'domain': [
                    ('id', 'in', draft_line_ids)
                ],
                'open_model': 'biote.stock.move',
                'exec_model': 'biote.stock.move'
            }
        }
        return action