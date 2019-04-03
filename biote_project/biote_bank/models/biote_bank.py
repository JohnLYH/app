import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class BioteBank(models.Model):
    _name = 'biote.bank'
    _description = '开户银行模型'

    name = fields.Char(string='开户银行')

