import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class RsStockValuation(models.TransientModel):
    _name = 'rs.stock.valuation'
    