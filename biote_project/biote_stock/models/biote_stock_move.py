import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class BioteStockMove(models.Model):
    _name = 'biote.stock.move'
    _description = '博益特库存移动单'

    name = fields.Char(string='描述', default='新建')
    product_id = fields.Many2one(comodel_name='product.product', string='产品名称')
    product_uom_id = fields.Many2one(related='product_id.uom_id')
    state = fields.Selection(
        string='入库单状态', selection=[('draft', '草稿'), ('done', '完成')], default='draft'
    )
    move_qty = fields.Float(string='移动数量')
    picking_id = fields.Many2one(comodel_name='biote.stock.picking', string='库存调拨')
    # 生成odoo库存移动单时，首先使用库位，如果没有指定则继续使用仓库的默认库位
    location_id = fields.Many2one(
        comodel_name='stock.location', string='源库位', help="当无法通过仓库指定库位时，通过该字段指定")
    dest_location_id = fields.Many2one(
        comodel_name='stock.location', string='目的库位', help="当无法通过仓库指定库位时，通过该字段指定")
    warehouse_id = fields.Many2one(comodel_name='stock.warehouse', string='源仓库')
    dest_warehouse_id = fields.Many2one(comodel_name='stock.warehouse', string='目的仓库')
    move_type = fields.Selection(
        string='库存移动类型', selection=[], help='表示库存移动类型')
    move_id = fields.Many2one(comodel_name='stock.move', string='odoo库存移动单')

    @api.model
    def create(self, vals):
        if vals.get('name', '新建') == '新建':
            # biote.stock.move的名称以 BMV_调拨单ID_产品ID 的形式组成
            picking_id = vals.get('picking_id')
            product_id = vals.get('product_id')
            name = 'BMV_%s_%s' % (picking_id, product_id)
            vals.update({'name': name})
        return super(BioteStockMove, self).create(vals)
    
    def _get_draft_moves(self):
        return self.filtered(lambda r: r.state == 'draft')

    def _get_src_location_id(self):
        # 自定义库存移动包含库位、仓库，通过该方法获取实际库位
        location_id = self.location_id or self.warehouse_id.lot_stock_id
        if not location_id:
            raise UserError('无法找到库存移动的源位置')
        return location_id

    def _get_dest_location_id(self):
        location_id = self.dest_location_id or self.dest_warehouse_id.lot_stock_id
        if not location_id:
            raise UserError('无法找到库存移动的目的位置')
        return location_id

    def _prepare_move_values(self):
        self.ensure_one()
        location_id = self._get_src_location_id()
        dest_location_id = self._get_dest_location_id()
        return {
            'name': self.name,
            'product_id': self.product_id.id,
            'product_uom': self.product_uom_id.id,
            'product_uom_qty': self.move_qty,
            'location_id': location_id.id,
            'scrapped': dest_location_id.scrap_location,
            'location_dest_id': dest_location_id.id,
            'move_line_ids': [(0, 0, {
                'product_id': self.product_id.id,
                'product_uom_id': self.product_uom_id.id, 
                'qty_done': self.move_qty,
                'location_id': location_id.id, 
                'location_dest_id': dest_location_id.id,
            })]
        }

    @api.multi
    def action_done(self):
        # 生成odoo移动单
        # 执行移动单完成操作
        for biote_mv in self:
            move = self.env['stock.move'].create(biote_mv._prepare_move_values())
            move._action_done()
            biote_mv.write({
                'state': 'done',
                'move_id': move.id
            })
