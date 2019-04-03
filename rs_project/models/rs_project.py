import logging
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class RsProject(models.Model):
    _name = 'rs.project'
    _description = '项目'
    _inherit = ['oa.workflow.mixin']

    name = fields.Char(string='项目')
    manager = fields.Many2one('res.users', default=lambda s: s.env.uid, string='负责人', readonly=True)
    line_ids = fields.One2many('rs.project.line', 'project_id', string='详情')


    def action_generate_purchase_contract(self):
        self.ensure_one()
        if self.workflow_state != 'done':
            raise UserError('项目未完成审批，不能生成采购合同！')
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'name': '采购合同',
            'view_id': self.env.ref('rs_project.rs_contract_view_form_wiz').id,
            'res_model': 'rs.contract',
            'context': {
                'default_project_id': self.id,
            },
            'target': 'new',
        }


class RsProjectLine(models.Model):
    _name = 'rs.project.line'
    _description = '项目明细'

    purchase_req_num = fields.Char('采购申请单号')
    product_id = fields.Many2one('product.product', string='名称')
    predict_qty = fields.Float(string='预估数量')
    uom = fields.Many2one('product.uom', string='单位')
    predict_price = fields.Float(string='预估单价')
    predict_total = fields.Float(string='预估总价', compute='_compute_predict_total')

    project_id = fields.Many2one('rs.project', ondelete='cascade', string='项目')

    @api.one
    @api.depends('predict_price', 'predict_qty')
    def _compute_predict_total(self):
        if self.predict_price:
            self.predict_total = self.predict_price * self.predict_qty
