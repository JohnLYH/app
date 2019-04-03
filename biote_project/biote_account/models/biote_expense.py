import logging

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
# from . import utils
from decimal import Decimal
from odoo.addons.biote_base import utils

_logger = logging.getLogger(__name__)


class BioteExpense(models.Model):
    _name = "biote.expense"

    name = fields.Char(string="单据编号", default='新建')
    employee_id = fields.Many2one('hr.employee', string="申请人")
    mediator_id = fields.Many2one('hr.employee', string="经办人",
                               default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)],
                                                                                   limit=1))
    expense_type = fields.Selection([('normal', '费用报销'), ('travel', '差旅报销')],
                                    default='normal', required=True, string="报销类型")
    company_id = fields.Many2one('res.company', string='公司', related='employee_id.company_id')
    department_id = fields.Many2one('hr.department', string='报销部门', related='employee_id.department_id')
    is_cash = fields.Boolean(string="是否现金报销")
    cash_amount = fields.Float(string="现金报销金额", digits=dp.get_precision('Biote Expense'))
    is_bank = fields.Boolean(string="是否银行报销")
    bank_amount = fields.Float(string="银行报销金额", digits=dp.get_precision('Biote Expense'))
    is_prepaid = fields.Boolean(string="是否冲预付报销")
    prepaid_amount = fields.Float(string="冲预付报销金额", digits=dp.get_precision('Biote Expense'))
    is_personal = fields.Boolean(string="是否冲个人报销")
    personal_amount = fields.Float(string="现冲个人销金额", digits=dp.get_precision('Biote Expense'))
    expense_line_ids = fields.One2many('biote.expense.line', 'biote_expense_id', string="报销详情项")
    total_amount = fields.Float(compute="_compute_total_amount", store=True, string='总金额',
                                digits=dp.get_precision('Biote Expense'))
    capital_total_amount = fields.Char(string="总金额大写", compute="_compute_capital_total_amount")
    receivables_company = fields.Char(string="收款单位（个人）")
    bank_id = fields.Many2one('biote.bank', string="开户行")
    receivables_account = fields.Char(string="收款账号")
    receivables_date = fields.Date(string="收款日期")
    note = fields.Text(string="备注")

    @api.model
    def create(self, vals):
        if vals.get('name', '新建') == '新建':
            next_code_tmp = 'biote.expense.num'
            if vals.get('expense_type', 'normal') == 'travel':
                next_code_tmp = 'biote.travel.expense.num'
            vals['name'] = self.env['ir.sequence'].next_by_code(next_code_tmp) or '/'
        return super(BioteExpense, self).create(vals)

    @api.depends('expense_line_ids', 'cash_amount', 'bank_amount', 'prepaid_amount', 'personal_amount')
    def _compute_total_amount(self):
        for record in self:
            tmp_total_amount = sum([Decimal(str(x)) for x in record.mapped('expense_line_ids.unit_amount')])
            reimburse_account = sum([Decimal(str(x)) for x in [record.cash_amount,
                                                               record.bank_amount,
                                                               record.prepaid_amount,
                                                               record.personal_amount]])
            if tmp_total_amount.compare(reimburse_account):
                raise ValidationError("已消费金额与报销金额不相等")
            record.total_amount = tmp_total_amount

    @api.depends("total_amount")
    def _compute_capital_total_amount(self):
        for record in self:
            record.capital_total_amount = utils.trans_capital_total_amount(record.total_amount)

    @api.onchange('is_cash', 'is_bank', 'is_prepaid', 'is_personal')
    def _onchange_amount(self):
        if not self.is_cash:
            self.cash_amount = 0
        if not self.is_bank:
            self.bank_amount = 0
        if not self.is_prepaid:
            self.prepaid_amount = 0
        if not self.is_personal:
            self.personal_amount = 0
