import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    lot_ids = fields.One2many(
        comodel_name='stock.production.lot', string='批次号', compute='_compute_lot_ids')
    selected_lot_location_ids = fields.One2many(
        comodel_name='stock.location', string='已用库位', compute='_compute_selected_lot_location_ids')
    sale_date = fields.Date(string='出库日期', required=True, readonly=True, index=True,
                            states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False,
                            default=fields.Date.today)

    @api.one
    @api.depends('order_line.lot_id', 'order_line.lot_location_id')
    def _compute_lot_ids(self):
        # 如果同一个产品同一库位的批次被两个订单行使用，这属于误操作
        # 这里假定每个库位批次出现在订单行中有两种情况：
        # 1. 满足需求 2. 不满足需求，耗尽，需要另开一行使用新的批次
        selected_lot_location_ids = self.order_line.mapped('lot_location_id')
        lot_ids = []
        for lot in self.order_line.mapped('lot_id'):
            lot_location_ids = lot.quant_ids.mapped('location_id').filtered(
                lambda r: r.usage in ['internal', 'transit'])
            # 如果批次的多个库位都被使用，则差集为空
            # 如果批次有未被使用的库位，则继续显示批次
            if not (lot_location_ids - selected_lot_location_ids):
                lot_ids.append(lot.id)
        self.lot_ids = lot_ids

    @api.one
    @api.depends('order_line.lot_location_id')
    def _compute_selected_lot_location_ids(self):
        self.selected_lot_location_ids = self.order_line.mapped('lot_location_id')

    @api.model
    def create(self, vals):
        if vals.get('name', '新建') == '新建':
            vals['name'] = self.env['ir.sequence'].next_by_code('sale.order.rs') or '/'
        return super(SaleOrder, self).create(vals)

    @api.multi
    def button_outgoing_confirm(self):
        if not self.order_line:
            raise UserError('未找到明细行')
        self.action_confirm()
        self.picking_ids.button_validate()

