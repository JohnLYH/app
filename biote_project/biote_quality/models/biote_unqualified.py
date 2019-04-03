import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero

_logger = logging.getLogger(__name__)


class BioteUnqualified(models.Model):
    _name = 'biote.unqualified'
    _description = '不合格品处置单'

    name = fields.Char(string='单据编号')
    product_id = fields.Many2one(comodel_name='product.product', string='产品名称')  
    handle_id = fields.Many2one(comodel_name='biote.unqualified.handle', string='不合格品处置方式')
    handle_qty = fields.Float(string='总处置数量')
    done_qty = fields.Float(string='已处置数量', compute='_compute_done_qty', store=True)
    remainging_qty = fields.Float(string='未处置数量', compute='_compute_done_qty', store=True)
    process_qty = fields.Float(string='处置中数量', compute='_compute_done_qty', store=True)
    can_handle_qty = fields.Float(string='可处置数量', compute='_compute_done_qty', store=True)
    state = fields.Selection(
        string='处置状态',
        selection=[('process', '处置中'), ('done', '处理完成')],
        compute='_compute_done_qty',
        store=True
    )
    refused_allow_id = fields.Many2one(comodel_name='biote.allow', string='未放行单号')
    # 不合格品入库单
    unqualified_incoming_id = fields.Many2one(comodel_name='biote.stock.picking', string='不合格品入库单')
    move_ids = fields.One2many(
        comodel_name='biote.stock.move', inverse_name='unqualified_id', string='库存移动')

    def _sum_done_qty(self):
        # 如果在其他模块中添加处置方式，可以复写该方法对done_qty的值进行累加
        done_moves = self.move_ids.filtered(lambda r: r.state == 'done')
        done_qty = sum(done_moves.mapped('move_qty'))
        # TODO: 退货单、销毁单完成的累加
        return done_qty

    def _sum_process_qty(self):
        process_moves = self.move_ids.filtered(lambda r: r.state == 'draft')
        process_qty = sum(process_moves.mapped('move_qty'))
        # TODO: 退货单、销毁单完成的累加
        return process_qty
    
    # 依赖于不合格品入库、退货、销毁等
    # 'move_ids.state' 数量与状态改变时都会触发计算方法
    @api.depends('handle_qty', 'move_ids.state')
    def _compute_done_qty(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for unqualified in self:
            unqualified.done_qty = unqualified._sum_done_qty()
            unqualified.process_qty = unqualified._sum_process_qty()
            unqualified.remainging_qty = unqualified.handle_qty - unqualified.done_qty
            unqualified.can_handle_qty = unqualified.remainging_qty - unqualified.process_qty
            if float_is_zero(unqualified.remainging_qty, precision):
                unqualified.state = 'done'
            else:
                unqualified.state = 'process'

    def action_done_wiz(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'name': '不合格处置',
            'res_model': 'biote.unqualified.done.wiz',
            'target': 'new',
            'context': {
                'default_unqualified_id': self.id,
                'default_can_handle_qty': self.can_handle_qty
            }
        }

    def _prepare_unqualified_handle_move(self, move_qty):
        return {
            'product_id': self.product_id.id,
            'move_qty': move_qty,
            'unqualified_id': self.id
        }
    
    def action_done(self, handle_id, handle_qty):
        self.ensure_one()
        self.write({
            'handle_id': handle_id.id
        })
        picking_type = handle_id.picking_type_id
        # TODO: 不是所有处置都会产生库存移动
        mv_vals = self._prepare_unqualified_handle_move(handle_qty)
        # 处置方式的usage与作业类型的code功能上有所耦合
        # 处置方式之所以存在，是考虑到有的处置方式不一定要有作业类型
        if handle_id.usage == 'incoming':
            # 不良品入库源位置是虚拟库位，目的位置是不良品仓库
            mv_vals.update({
                'location_id': picking_type.location_id.id,
                'dest_warehouse_id': picking_type.dest_warehouse_id.id
            })
        elif handle_id.usage in ('return', 'scrap'):
            # 不良品退货与报废的源与目的位置都是虚拟位置
            mv_vals.update({
                'location_id': picking_type.location_id.id,
                'dest_location_id': picking_type.dest_location_id.id
            })
        picking_vals = {
            'move_ids': [(0, 0, mv_vals)],
            'picking_type_id': handle_id.picking_type_id.id,
        }
        self.env['biote.stock.picking'].create(picking_vals)
