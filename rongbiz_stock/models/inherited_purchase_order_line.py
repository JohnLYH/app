import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    lot_name = fields.Char('批次号')
    project_id = fields.Many2one('rs.project', string='所属项目', required=True)
    purchase_date = fields.Date(related='order_id.purchase_date', string='入库日期', store=True)
    invoice_category = fields.Selection(related='order_id.invoice_category', string='发票类别', store=True)
    note = fields.Char(string='备注')
    predict_price = fields.Float(string='预估单价')
    predict_total = fields.Float(string='预估总价', compute='_compute_predict_total')

    @api.onchange('predict_price')
    def _onchange_predict_price(self):
        self.price_unit = self.predict_price

    @api.one
    @api.depends('predict_price', 'product_qty')
    def _compute_predict_total(self):
        if self.predict_price:
            self.predict_total = self.predict_price*self.product_qty


class RsProject(models.Model):
    _name = 'rs.project'

    name = fields.Char(string='项目')

