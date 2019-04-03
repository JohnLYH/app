import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class BiotePurchaseRecevie(models.Model):
    _name = 'biote.purchase.recevie'
    _inherit = ['biote.base.model']
    _description = '采购收货四联单'

    name = fields.Char(string='单据编号')
    order_date = fields.Date(string='单据日期')
    contract_id = fields.Many2one(
        comodel_name='biote.contract',
        string='合同号', 
        domain=[('category', '=', 'purchase_raw'), ('biote_audit_state', '=', 'done')]
    )
    qa_dep_id = fields.Many2one(comodel_name='hr.department', string='请验部门')
    qa_date = fields.Datetime(string='请验日期')
    recevie_user_id = fields.Many2one(
        comodel_name='res.users', default=lambda self: self.env.uid, string='物料收货人')
    recevie_line_ids = fields.One2many(
        comodel_name='biote.purchase.recevie.line', inverse_name='recevie_id', string='收货明细')

    @api.onchange('contract_id')
    def onchange_order_id(self):
        self.recevie_line_ids = self.contract_id.biote_purchase_plan_id.line_ids.mapped(
            lambda r: (0, 0, {
                'product_id': r.product_id.id,
                'ordered_qty': r.planned_purchase_amount,
                'allow_state': 'draft' # 通过onchange创建的收货明细，需要显示设置默认值，否则为False
            })
        )

    @api.multi
    def action_raw_allow_select_dialog(self):
        self.ensure_one()
        raw_allow_line_ids = self.recevie_line_ids._get_allow_line()
        action = {
            'type': 'ir.actions.client',
            'tag': 'select_dialog',
            'context': {
                'title': '选择收货单明细',
                'method': 'action_create_raw_allow', 
                'domain': [
                    ('id', 'in', raw_allow_line_ids.ids)
                ],
                'open_model': 'biote.purchase.recevie.line',
                'exec_model': 'biote.purchase.recevie.line'
            }
        }
        return action

    @api.multi
    def action_unqualified_select_dialog(self):
        self.ensure_one()
        # 列表对话框显示收货四联单所有行可以下推不合格处置单的不放行单
        unqualified_allow_ids = self.recevie_line_ids.mapped('raw_allow_ids')._get_unqualified_allow().ids
        action = {
            'type': 'ir.actions.client',
            'tag': 'select_dialog',
            'context': {
                'title': '选择单据',
                'method': 'action_create_unqualified',
                'domain': [
                    ('id', 'in', unqualified_allow_ids)
                ],
                'open_model': 'biote.allow',
                'exec_model': 'biote.allow'
            }
        }
        return action

    @api.multi
    def action_incoming_select_dialog(self):
        self.ensure_one()
        # 列表对话框显示收货四联单所有行关联的不放行状态的放行单
        incoming_allow_ids = self.recevie_line_ids.mapped('raw_allow_ids')._get_incoming_allow().ids
        action = {
            'type': 'ir.actions.client',
            'tag': 'select_dialog',
            'context': {
                'title': '选择单据',
                'method': 'action_create_incoming',
                'domain': [
                    ('id', 'in', incoming_allow_ids)
                ],
                'open_model': 'biote.allow',
                'exec_model': 'biote.allow'
            }
        }
        return action