import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class BioteAllowItem(models.Model):
    _inherit = 'biote.allow.item'
    
    categ = fields.Selection(selection_add=[('raw', '原材料放行单')])
