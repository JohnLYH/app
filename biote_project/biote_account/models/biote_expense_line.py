import logging

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from decimal import Decimal

_logger = logging.getLogger(__name__)


class BioteExpenseLine(models.Model):
    _name = "biote.expense.line"

    name = fields.Char(string="名称")
    cause = fields.Char(string="事由")
    biote_expense_id = fields.Many2one('biote.expense', string="绑定报销单")
    unit_amount = fields.Float(string='金额', required=True, digits=dp.get_precision('Biote Expense'))

    start_position = fields.Char(string="起点")
    end_position = fields.Char(string="终点")

    ticket_qty = fields.Integer(string="车船票数量")
    ticket_unit = fields.Float(string="车船票单价", digits=dp.get_precision('Biote Expense'))
    ticket_subtotal = fields.Float(string="车船票小计", digits=dp.get_precision('Biote Expense'))

    room_qty = fields.Integer(string="住宿数量")
    room_unit = fields.Float(string="住宿单价", digits=dp.get_precision('Biote Expense'))
    room_subtotal = fields.Float(string="住宿小计", digits=dp.get_precision('Biote Expense'))

    traffic_subsidy_qty = fields.Integer(string="交通补贴天数")
    traffic_subsidy_unit = fields.Float(string="交通补贴单价", digits=dp.get_precision('Biote Expense'))
    traffic_subsidy_subtotal = fields.Float(string="交通补贴小计", digits=dp.get_precision('Biote Expense'))

    food_subsidy_qty = fields.Integer(string="午餐补贴天数")
    food_subsidy_unit = fields.Float(string="午餐补贴单价", digits=dp.get_precision('Biote Expense'))
    food_subsidy_subtotal = fields.Float(string="午餐补贴小计", digits=dp.get_precision('Biote Expense'))
    other_subtotal = fields.Float(string="其他花费", digits=dp.get_precision('Biote Expense'))

    @api.onchange('ticket_qty', 'ticket_unit', 'ticket_subtotal',
                  'room_qty', 'room_unit', 'room_subtotal',
                  'traffic_subsidy_qty', 'traffic_subsidy_unit', 'traffic_subsidy_subtotal',
                  'food_subsidy_qty', 'food_subsidy_unit', 'food_subsidy_subtotal',
                  'other_subtotal')
    def _onchange_total(self):
        self.ticket_subtotal = Decimal(str(self.ticket_qty)) * Decimal(str(self.ticket_unit))
        self.room_subtotal = Decimal(str(self.room_qty)) * Decimal(str(self.room_unit))
        self.traffic_subsidy_subtotal = Decimal(str(self.traffic_subsidy_qty)) * Decimal(
            str(self.traffic_subsidy_unit))
        self.food_subsidy_subtotal = Decimal(str(self.food_subsidy_qty)) * Decimal(
            str(self.food_subsidy_unit))
        tmp_total_amount = sum([Decimal(str(x)) for x in [self.ticket_subtotal, self.room_subtotal,
                                                          self.traffic_subsidy_subtotal,
                                                          self.food_subsidy_subtotal,
                                                          self.other_subtotal]])
        if tmp_total_amount > 0:
            self.unit_amount = tmp_total_amount
