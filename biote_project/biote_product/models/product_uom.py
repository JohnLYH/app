import logging
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ProductUom(models.Model):
    _inherit = 'product.uom'

    uom_num = fields.Char('计量单位编码', default='新建')
    company_id = fields.Many2one('res.company', string='公司', default=lambda self: self.env.user.company_id,
                                 readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('uom_num', '新建') == '新建':
            vals['uom_num'] = self.env['ir.sequence'].next_by_code('product.uom.num') or '/'
        return super(ProductUom, self).create(vals)
