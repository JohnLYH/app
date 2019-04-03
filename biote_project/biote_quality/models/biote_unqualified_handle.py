import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class BioteUnqualifiedHandle(models.Model):
    _name = 'biote.unqualified.handle'
    _description = '不合格处置方式'

    name = fields.Char(string='名称')
    usage = fields.Selection(
        string='处置类型',
        selection=[
            ('return', '不良品退货'),
            ('incoming', '不良品入库'),
            ('scrap', '销毁'),
            ('other', '其他')
        ]
    )
    picking_type_id = fields.Many2one(comodel_name='biote.stock.picking.type', string='作业类型')
    