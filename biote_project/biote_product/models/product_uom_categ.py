import logging
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ProductUomCateg(models.Model):
    _inherit = 'product.uom.categ'

    active = fields.Boolean('有效否', default=True)
    uom_categ_num = fields.Char('计量单位类别编码', default='新建')
    company_id = fields.Many2one('res.company', string='公司', default=lambda self: self.env.user.company_id,
                                 readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('uom_categ_num', '新建') == '新建':
            vals['uom_categ_num'] = self.env['ir.sequence'].next_by_code('product.uom.categ.num') or '/'
        return super(ProductUomCateg, self).create(vals)
