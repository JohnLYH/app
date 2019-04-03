import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    specification = fields.Char(string='规格')
    lot_qty = fields.Float(string='在手数量', compute='_compute_lot_qty')
    lot_available_qty = fields.Float(string='可用数量', compute='_compute_lot_qty')
    lot_reserved_qty = fields.Float(string='锁定数量', compute='_compute_lot_qty')
    lot_valuation = fields.Float(string='不含税价值', compute='_compute_lot_qty')
    lot_valuation_tax = fields.Float(string='含税价值', compute='_compute_lot_qty')
    readonly_all = fields.Boolean(string='所有字段只读', default=True)
    average_value = fields.Float(string='平均价格', compute='_compute_lot_qty')
    product_eval = fields.Selection([
        ('worthless', '无价值'),
        ('general', '一般'),
        ('ordinary', '普通'),
        ('precious', '贵重'),
        ('expensive', '昂贵')],
        string='产品价值', compute='_compute_product_eval')

    @api.one
    def _compute_lot_qty(self):
        lot_ids = self.env['stock.production.lot'].search([('product_id', '=', self.id)])
        self.lot_qty = sum(lot_ids.mapped('product_qty'))
        self.lot_available_qty = sum(lot_ids.mapped('product_available_qty'))
        self.lot_reserved_qty = sum(lot_ids.mapped('product_reserved_qty'))
        self.lot_valuation_tax = sum(lot_ids.mapped('lots_valuation_included'))
        self.lot_valuation = sum(lot_ids.mapped('lot_valuation_excluded'))
        self.average_value = self.lot_qty and self.lot_valuation/self.lot_qty

    @api.one
    @api.depends('average_value')
    def _compute_product_eval(self):
        if self.average_value > 0:
            if 0 < self.average_value < 50:
                self.product_eval = 'general'
            elif 50 < self.average_value < 100:
                self.product_eval = 'ordinary'
            elif 100 < self.average_value < 2000:
                self.product_eval = 'precious'
            else:
                self.product_eval = 'expensive'
        else:
            self.product_eval = 'worthless'

