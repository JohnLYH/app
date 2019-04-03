import logging
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)


class BioteAssetsPurchase(models.Model):
    # _inherit = ['oa.workflow.mixin']
    _name = 'biote.assets.purchase'

    purchase_req_num = fields.Char('单据编号', default='新建')
    name = fields.Char('资产名称', required=True)
    specification_model = fields.Char('规格型号', required=True)
    brand = fields.Char('品牌')
    quantity = fields.Float('购置数量', digits=dp.get_precision('Biote Purchase'), required=True)
    estimated_amount = fields.Float('预计金额', digits=dp.get_precision('Biote Purchase'))
    budget_amount = fields.Float('预算金额', digits=dp.get_precision('Biote Purchase'))
    uom = fields.Char('单位', required=True)
    demand_date = fields.Date('需求日期', required=True)
    purchase_req_date = fields.Date('请购日期')
    purchase_reason = fields.Char('购置原因', required=True)
    expected_result = fields.Char('预期效果')
    budget_or_not = fields.Boolean(string='有无预算', default=False)
    req_dep = fields.Many2one('hr.department', '申请部门', required=True)
    mediator = fields.Many2one('hr.employee', '经办人', required=True)
    attachment = fields.Binary('附件')
    price_rel = fields.Boolean('比价', default=False)
    contract = fields.Boolean('合同', default=False)
    direct = fields.Boolean('直接采购', default=True)

    @api.model
    def create(self, vals):
        if vals.get('purchase_req_num', '新建') == '新建':
            vals['purchase_req_num'] = self.env['ir.sequence'].next_by_code('biote.assets.purchase.num')
        return super(BioteAssetsPurchase, self).create(vals)

    @api.constrains('budget_or_not', 'budget_amount')
    def _check_budget(self):
        for rec in self:
            if rec.budget_or_not and rec.budget_amount == 0:
                raise ValidationError('你选择了有预算,请填写正确的预算金额!')

    @api.onchange('budget_or_not')
    def _onchange_budget_or_not(self):
        if not self.budget_or_not:
            self.budget_amount = 0
