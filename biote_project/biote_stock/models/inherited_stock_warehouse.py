import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    sequence = fields.Integer(string='优先级', default=16)
    biote_warehouse_type = fields.Selection(
        string='仓库类型',
        selection=[
            ('raw', '原材料'), # 原材料采购入库使用该仓库
            ('unqualified_raw', '不合格原材料') # 原材料采购，不合格入库使用该仓库
        ]
    )

    def _get_raw_warehouse(self):
        raw_warehouse = self.search(
            [('biote_warehouse_type', '=', 'raw')], order='sequence asc', limit=1)
        if not raw_warehouse:
            raise UserError('未配置原材料收货仓库')

    # 调整stock.move使用处的仓库信息