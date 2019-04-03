import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class StockLocation(models.Model):
    _inherit = 'stock.location'

    sequence = fields.Integer(string='优先级', default=16)
    is_recevie_location = fields.Boolean(string='来料收货位置', help='来料收货位置是一个虚拟库位')

    def _get_recevie_location(self):
        # 获取收货库位
        recevie_location = self.env['stock.location'].search(
            [('is_recevie_location', '=', True)], order='sequence asc', limit=1)
        if not recevie_location:
            raise UserError('没有配置来料收货位置！')
        return recevie_location