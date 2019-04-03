import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    purchase_date = fields.Date(string='入库日期', required=True, states=READONLY_STATES, index=True, copy=False,
                                default=fields.Date.today)
    invoice_category = fields.Selection([('special_vote', '增值税专用发票'),
                                        ('general_vote', '增值税普通发票'),
                                        ('temporary', '暂估')], string='发票类别', default='temporary', required=True)
    is_verify = fields.Boolean(string='验证发票', default=True)
    predict_total_price = fields.Float(string='暂估总计', compute='_compute_predict_total_price')

    @api.model
    def create(self, vals):
        if vals.get('name', '新建') == '新建':
            vals['name'] = self.env['ir.sequence'].next_by_code('purchase.order.rs') or '/'
        return super(PurchaseOrder, self).create(vals)

    @api.multi
    def button_incoming_confirm(self):
        if not self.order_line:
            raise UserError('未找到明细行')
        for line in self.order_line:
            if line.product_qty <= 0:
                raise ValidationError('%s的入库数量不能为负数' % line.product_id.name)
        # 采购订单确认
        self.button_confirm()
        # 捡货订单确认
        self.picking_ids.button_validate()

    @api.multi
    def verify_invoice(self):
        if self.invoice_category == 'temporary':
            raise UserError('请修改发票类别!')
        else:
            for p in self.order_line:
                if p.taxes_id:
                    self.is_verify = False
                    records = self.env['stock.production.lot'].search([
                        ('name', '=', p.lot_name), ('product_id', '=', p.product_id.id)]).sale_order_line_ids
                    if records:
                        for r in records:
                            r.tax_id, r.price_unit = p.taxes_id, p.price_unit
                else:
                    raise UserError('税率不能为空!')
        return True

    @api.onchange('invoice_category')
    def _onchange_taxes_id(self):
        for r in self.order_line:
            r.taxes_id = False

    @api.depends('order_line.predict_price', 'order_line.product_qty')
    def _compute_predict_total_price(self):
        self.predict_total_price = sum(self.order_line.mapped(lambda r: r.predict_price*r.product_qty))

