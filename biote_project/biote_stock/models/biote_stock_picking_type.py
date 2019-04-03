import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

# 博益特不使用库位，使用仓库进行货品管理，odoo原生库存移动单使用库位进行移动
# 使用仓库的默认库位作为对应的库位，不使用related进行关联，使用onchange
class BioteStockPickingType(models.Model):
    _name = 'biote.stock.picking.type'
    _description = '博益特作业类型'

    name = fields.Char(string='作业名称')
    location_id = fields.Many2one(comodel_name='stock.location', string='源库位')
    dest_location_id = fields.Many2one(comodel_name='stock.location', string='目的库位')
    warehouse_id = fields.Many2one(comodel_name='stock.warehouse', string='源仓库')
    dest_warehouse_id = fields.Many2one(comodel_name='stock.warehouse', string='目的仓库')
    code = fields.Selection([('internal', '内部调拨')], '作业编码')
    sequence = fields.Integer(string='优先级', default=16)
    
    def _get_specific_type(self, code):
        raw_incoming_type = self.env['biote.stock.picking.type'].search(
            [('code', '=', code)], order='sequence asc', limit=1)
        if not raw_incoming_type:
            raise UserError('没有配置收货作业类型！')
        return raw_incoming_type