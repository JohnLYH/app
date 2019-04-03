import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def create(self, vals):
        return super(ResUsers, 
        self.with_context(default_customer=False, default_supplier=False)).create(vals)
