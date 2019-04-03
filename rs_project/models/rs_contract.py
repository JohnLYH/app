import logging
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class RsContract(models.Model):
    _name = 'rs.contract'
    _description = '合同'
    _inherit = ['oa.workflow.mixin']

    num = fields.Char(string='合同编号', default='新建')
    date = fields.Date(string='发起日期', default=fields.Date.today)
    name = fields.Char(string='合同名称')
    content = fields.Text(string="合同概要")
    party_a = fields.Char(string='甲方', required=True, default='青岛容商天下网络有限公司')
    party_b = fields.Char(string='乙方', required=True)
    amount = fields.Float(string='合同金额', required=True)
    sponsor_id = fields.Many2one('res.users', default=lambda s: s.env.uid, string='发起人')

    project_id = fields.Many2one('rs.project', string='关联项目')