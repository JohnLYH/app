import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp
_logger = logging.getLogger(__name__)


# 用户选择产品，然后根据产品关联出相关批次
# 用户选择批次后，关联出批次quant所在的库位信息
# 用户选择库位后根据产品、批次、库位获取有效数量
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    lot_id = fields.Many2one('stock.production.lot', '批次号')
    product_available_qty = fields.Float(string='可用库存', compute='_compute_product_available_qty')
    # product_reserved_qty = fields.Float(related='lot_id.product_reserved_qty')
    incoming_price = fields.Float(related='lot_id.incoming_price', string='单价', help='入库价格(采购单价) = 销售单价')
    lot_location_id = fields.Many2one(comodel_name='stock.location', string='出货库位')
    lot_location_ids = fields.One2many(
        comodel_name='stock.location',  string='批次有效库位', compute='_compute_lot_location_ids')
    project_id = fields.Many2one(related='lot_id.project_id', string='所属项目', store=True)
    invoice_category = fields.Selection(related='lot_id.invoice_category', string='发票类别', store=True)
    # sale_tax_ids = fields.Many2many(related='lot_id.taxes_id', string='税率', domain=[])
    sale_date = fields.Date(related='order_id.sale_date', string='出库日期', store=True)
    note = fields.Char(string='备注')

    @api.one
    @api.depends('product_id', 'lot_id', 'lot_location_id')
    def _compute_product_available_qty(self):
        # _get_available_quantity返回该产品,该批次,该库位的可用数量
        product_available_qty = self.env['stock.quant']._get_available_quantity(
            self.product_id, self.lot_location_id, self.lot_id)
        self.product_available_qty = product_available_qty or 0

    @api.depends('lot_id')
    def _compute_lot_location_ids(self):
        for r in self:
            r.lot_location_ids = r.lot_id.quant_ids.filtered(
                lambda r: r.location_id.usage in ['internal', 'transit']).mapped('location_id')

    @api.onchange('product_uom_qty')
    def _onchange_product_uom_qty(self):
        if self.product_id and self.lot_id and (self.product_uom_qty > self.product_available_qty):
            self.product_uom_qty = self.product_available_qty
            return {
                'warning': {'title': "批次库存不足", 'message': "需求数量超过库位中该批次数量的最大值！"},
            }

    @api.onchange('incoming_price')
    def _onchange_incoming_price(self):
        if self.lot_id:
            # 入库价格(采购单价) = 销售单价
            self.price_unit = self.incoming_price

    @api.onchange('lot_id')
    def _onchange_tax_id(self):
        if self.lot_id:
            # ids = [(4, r.id, 0) for r in self.lot_id.taxes_id]
            # ids.insert(0, (5, 0, 0))
            # self.tax_id = ids
            self.tax_id = self.lot_id.taxes_id

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        # 跳过价格表获取产品价格的流程
        pass
