import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class BioteCustomerCategory(models.Model):
    _name = 'biote.customer.category'
    _description = '客户分类模型'

    name = fields.Char(string='名称')
