import logging
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)


class BiotePurchasePlan(models.Model):
    _name = 'biote.purchase.plan'
    _inherit = ['oa.workflow.mixin', 'biote.base.model']
    _rec_name = 'doc_num'

    doc_num = fields.Char('单据编号', default='新建')
    line_ids = fields.One2many('biote.purchase.plan.line', 'plan_id', string='详情')
    department = fields.Many2one('hr.department', '部门')
    budget_amount_total = fields.Float(
        string='预算总量',
        store=True, 
        readonly=True,
        compute='_compute_amount_all',
        digits=dp.get_precision('Biote Purchase')
    )
    inventory_amount_total = fields.Float(
        string='库存总量',
        store=True,
        readonly=True,
        compute='_compute_amount_all',
        digits=dp.get_precision('Biote Purchase')
    )
    planned_purchase_amount_total = fields.Float(
        string='计划采购总量',
        store=True,
        readonly=True,
        compute='_compute_amount_all',
        digits=dp.get_precision('Biote Purchase')
    )
    contract_ids = fields.One2many(
        comodel_name='biote.contract', inverse_name='biote_purchase_plan_id', string='采购合同审批')
    

    @api.model
    def create(self, vals):
        if vals.get('doc_num', '新建') == '新建':
            vals['doc_num'] = self.env['ir.sequence'].next_by_code('biote.purchase.plan.num')
        return super(BiotePurchasePlan, self).create(vals)

    @api.depends('line_ids.budget_amount', 'line_ids.inventory', 'line_ids.planned_purchase_amount')
    def _compute_amount_all(self):
        for rec in self:
            rec.budget_amount_total = sum(rec.mapped('line_ids.budget_amount'))
            rec.inventory_amount_total = sum(rec.mapped('line_ids.inventory'))
            rec.planned_purchase_amount_total = sum(rec.mapped('line_ids.planned_purchase_amount'))

    def action_generate_purchase_contract(self):
        self.ensure_one()
        if self.workflow_state != 'done':
            raise UserError('采购计划未完成审批，不能生成采购合同！')
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'name': '原材料采购合同',
            'res_model': 'biote.contract',
            'view_id': self.env.ref('biote_contract.biote_contract_view_form_wiz').id,
            'context': {
                'default_biote_purchase_plan_id': self.id,
                'default_category': 'purchase_raw'
            },
            'target': 'new',
        }


class BiotePurchasePlanLine(models.Model):
    _name = 'biote.purchase.plan.line'

    purchase_req_num = fields.Char('采购申请单号', related='plan_id.doc_num')
    product_code = fields.Char('产品代号', related='product_id.product_code')
    product_id = fields.Many2one('product.product', string='物料名称')
    specification = fields.Char('规格型号', related='product_id.specification')
    budget_amount = fields.Float('预算量', digits=dp.get_precision('Biote Purchase'))
    inventory = fields.Float('库存量', digits=dp.get_precision('Biote Purchase'))
    planned_purchase_amount = fields.Float('计划采购量', digits=dp.get_precision('Biote Purchase'))
    uom = fields.Many2one('product.uom', string='单位')
    demand_date = fields.Date('需求时间')
    manufacturer_permit = fields.Char('生产企业许可证', related='product_id.manufacturer_permit')
    plan_id = fields.Many2one('biote.purchase.plan', ondelete='cascade', string='计划')

    def action_show_details(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'name': '计划详情',
            'res_model': 'biote.purchase.plan',
            'res_id': self.plan_id.id,
            'target': 'new',
        }
        return action
