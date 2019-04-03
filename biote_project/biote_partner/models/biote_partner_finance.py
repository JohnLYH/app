import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class BiotePartnerFinance(models.Model):
    _name = 'biote.partner.finance'
    _description = '合作伙伴财务信息模型'

    name = fields.Char(string='开户名称', required=True)
    partner_id = fields.Many2one('res.partner', string='所属企业')
    bank_name = fields.Many2one('biote.bank', string='开户银行', required=True)
    account_num = fields.Char(string='银行账号', required=True)

