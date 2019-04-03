import logging

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    stock_move_line_ids = fields.One2many(comodel_name='stock.move.line', inverse_name='lot_id', string='关联移动明细')
    #  lot -> many stock.move.line -> one stock.move -> one purchase.order.line
    incoming_price = fields.Float(
        string='入库价格', digits=dp.get_precision('Product Price'), 
        related='stock_move_line_ids.move_id.purchase_line_id.price_unit', store=True
    )
    product_available_qty = fields.Float(
        string='可用库存', help='批次中的有效数量', compute='_compute_lot_product_qty', store=True
    )
    product_reserved_qty = fields.Float(
        string='已锁定库存', help='批次中保留的数量', compute='_compute_lot_product_qty', store=False
    )
    sale_order_line_ids = fields.One2many('sale.order.line', 'lot_id', help='批次号对应的销售订单行')
    # def _search_product_available_qty(self, operator, value):
    #     # 搜索有效库存大于0的批次号
    #     if operator == '>' and value is 0:
    #         ids = []
    #         for r in self:
    #             quants = r.quant_ids.filtered(lambda q: q.location_id.usage in ['internal', 'transit'])
    #             if (sum(quants.mapped('quantity')) - sum(quants.mapped('reserved_quantity'))) > 0:
    #                 ids.append(r.id)
    #         return [('id', 'in', ids)]
    # stock_move_line_ids(stock.production.lot) -> move_id(stock.move.line) -> purchase_line_id(stock.move) ->
    # ->order_id(.order.line) ->invoice_category(purchase.order)
    invoice_category = fields.Selection(
        related='stock_move_line_ids.move_id.purchase_line_id.invoice_category', string='发票类别', store=True)
    project_id = fields.Many2one(
        related='stock_move_line_ids.move_id.purchase_line_id.project_id', string='所属项目', store=True)
    lots_valuation_included = fields.Float(
        string='含税价值', help='该批次的含税价值', compute='_compute_lots_total_included', store=True)
    lot_valuation_excluded = fields.Float(
        string='不含税价值', help='该批次的不含税价值', compute='_compute_lots_total_included', store=True)
    taxes_id = fields.Many2many(
        related='stock_move_line_ids.move_id.purchase_line_id.taxes_id', string='税率')

    @api.one
    @api.depends('quant_ids.reserved_quantity', 'quant_ids.quantity')
    def _compute_lot_product_qty(self):
        quants = self.quant_ids.filtered(lambda q: q.location_id.usage in ['internal', 'transit'])
        self.product_reserved_qty = sum(quants.mapped('reserved_quantity'))
        self.product_available_qty = sum(quants.mapped('quantity')) - self.product_reserved_qty

    @api.one
    @api.depends('incoming_price', 'product_available_qty', 'taxes_id')
    def _compute_lots_total_included(self):
        ret = self.taxes_id.compute_all(
                price_unit=self.incoming_price,
                quantity=self.product_available_qty)
        self.lots_valuation_included = ret.get('total_included')
        self.lot_valuation_excluded = ret.get('total_excluded')



