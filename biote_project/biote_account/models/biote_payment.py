import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp
from odoo.addons.biote_base import utils

_logger = logging.getLogger(__name__)


class BiotePayment(models.Model):
    _name = 'biote.payment'

    company_id = fields.Many2one('res.company', string='公司', related='mediator_id.company_id')
    name = fields.Char(string="单据编号", default='新建')
    doc_type = fields.Selection([('prepayments', '预付款'), ('personal', '个人借款')], string="单据类型")
    supplier = fields.Char(string="供应商")
    bank_id = fields.Many2one('biote.bank', string="开户行")
    receivables_account = fields.Char(string="收款账号")
    apply = fields.Text(string="用途")
    mediator_id = fields.Many2one(
        'hr.employee',
        string="经办人",
        default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1))
    payment_type = fields.Selection([
        ('check', '支票'),
        ('cash', '现金'),
        ('wireTransfer', '电汇'),
        ('OnlineBank', '网银转账'),
        ('BankDraft', '银行汇票'),
        ('BankCashiers', '银行本票'),
        ('CommercialDraft', '商业汇票')
    ], string="支付方式")
    total_amount = fields.Float(string='总金额', digits=dp.get_precision('Biote Expense'))
    capital_total_amount = fields.Char(string="总金额大写", compute="_compute_capital_total_amount")
    settlement_certificate = fields.Selection([('invoice', '发票'), ('receipt', '收据')], string="结算凭证")
    check_num = fields.Char(string='支票号码')
    receivables_date = fields.Date(string="收款日期")
    receivables_company = fields.Char(string="收款单位（个人）")

    @api.depends("total_amount")
    def _compute_capital_total_amount(self):
        for record in self:
            record.capital_total_amount = utils.trans_capital_total_amount(record.total_amount)

    @api.model
    def create(self, vals):
        if vals.get('name', '新建') == '新建':
            vals['name'] = self.env['ir.sequence'].next_by_code('biote.payment.num') or '/'
        return super(BiotePayment, self).create(vals)

    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        if self.payment_type != 'check':
            self.check_num = None
