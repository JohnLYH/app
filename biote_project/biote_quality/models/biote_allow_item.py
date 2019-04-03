import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class BioteAllowItem(models.Model):
    _name = 'biote.allow.item'
    _description = '放行审核内容'

    name = fields.Char(string='审核内容')
    categ = fields.Selection(
        string='放行单类别',
        selection=[]
    )
    