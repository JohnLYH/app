import logging
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ProductCategory(models.Model):
    _inherit = 'product.category'

    classification_code = fields.Char('产品分类编码')
    complete_cls_code = fields.Char('完整产品分类编码', compute='_compute_cls_code', store=True)
    active = fields.Boolean('有效否', default=True)
    company_id = fields.Many2one('res.company', string='公司', default=lambda self: self.env.user.company_id,
                                 readonly=True)

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = '%s-%s' % (category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name

    @api.depends('classification_code', 'parent_id.complete_cls_code')
    def _compute_cls_code(self):
        for category in self:
            if category.parent_id:
                category.complete_cls_code = '%s-%s' % (
                    category.parent_id.complete_cls_code, category.classification_code)
            else:
                category.complete_cls_code = category.classification_code
