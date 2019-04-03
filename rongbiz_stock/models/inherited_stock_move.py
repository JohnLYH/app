from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        vals = super(StockMove, self)._prepare_move_line_vals(quantity, reserved_quant)
        # 根据采购或者销售设置批次名称（新建）或者批次号（已创建）
        # TODO: 采购应该可以更新批次数量，两个入库单是同一批次产品
        vals.update({
            # 省略了数量验证环节，默认库单确认时，所有货品都是已收货(采购数量等于收货数量)
            'qty_done': vals.get('product_uom_qty', 0.0)
        })
        if self.picking_code == 'incoming':
            vals.update({'lot_name': self.purchase_line_id.lot_name})
        # 可以在采购入库单中设置入库库位，然后替换vals中相应的值
        # 出库时注意如果选择了批次，会使用批次保留quant的库位作为源库位，无需在销售出库单中设置库位
        # 更改入库位置
        # * 产品类别（上架策略），可以更改系统流程，无需使用目的库位的上架策略，只是根据类别搜索上架位置即可
        # * 产品（需开发）
        # * 订单行（需开发，优先级最高）
        return vals

    def _update_reserved_quantity(self, need, available_quantity,
                                  location_id, lot_id=None, package_id=None, owner_id=None, strict=True):
        # 销售出库时需要根据销售订单行使用的批次来更新锁定库存
        if self.picking_code == 'outgoing' and self.sale_line_id:
            lot_id = self.sale_line_id.lot_id
        return super(StockMove, self)._update_reserved_quantity(need, available_quantity,
                                                                location_id, lot_id, package_id, owner_id, strict)
