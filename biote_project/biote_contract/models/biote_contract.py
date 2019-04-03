import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class BioteContract(models.Model):
    _name = 'biote.contract'
    _description = '合同签约审批表'
    _inherit = ['oa.workflow.mixin', 'biote.base.model']

    num = fields.Char(string='合同编号', default='新建')
    date = fields.Date(string='发起日期', default=fields.Date.today)
    category = fields.Selection([
        ('sale', '销售合同-院线'),
        ('sale_otc', '销售合同-otc'),
        ('purchase_raw', '采购合同-原材料/辅料'),
        ('purchase_assets', '采购合同-固定资产'),
        ('service', '服务合同')
    ], string='合同类别')
    name = fields.Char(string='合同名称')
    content = fields.Text(string="合同概要")
    party_a = fields.Char(string='甲方', required=True, default='青岛博益特生物材料股份有限公司')
    party_b = fields.Char(string='乙方', required=True)
    fname = fields.Char(string='合同名称')
    data = fields.Binary(string='合同附件', required=True)
    amount = fields.Float(string='合同金额', required=True)
    sponsor_id = fields.Many2one('res.users', default=lambda s: s.env.uid, string='发起人')

    @api.model
    def create(self, vals):
        if vals.get('num', '新建') == '新建':
            vals['num'] = self.env['ir.sequence'].next_by_code('biote.contract')
        return super(BioteContract, self).create(vals)

    def print_contract(self):
        return {
            "name": '预览报表',
            "type": "ir.actions.act_url",
            "url": "/report/pdf/biote_contract.biote_contract_templates/%d" % self.id,
            "target": "new",
        }
