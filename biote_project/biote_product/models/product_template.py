import logging
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    company_id = fields.Many2one('res.company', string='公司', default=lambda self: self.env.user.company_id,
                                 readonly=True)
    product_code = fields.Char('产品代码', default='新建')
    complete_product_code = fields.Char('完整产品代码', compute='_compute_code')
    specification = fields.Char('规格型号')
    reg_account = fields.Char('注册证号')
    manufacturer_permit = fields.Char('生产企业许可证')
    manufacturer = fields.Many2one('res.partner', '生产企业')
    barcode = fields.Char('产品条码')
    hs_code = fields.Char('HS编码')
    product_status = fields.Selection(selection=[('enable', '启用'), ('disable', '禁用'), ],
                                      default='enable', string="产品状态", )
    storage = fields.Selection(selection=[('refrigeration', '冷藏'), ], string='储藏条件')
    trace_back = fields.Selection(selection=[('batch_no', '批次号'), ('no_tracking_info', '无追踪信息'), ],
                                  default='batch_no', string="追溯", )
    input_tax = fields.Many2one('account.tax', string='进项税', domain=[('type_tax_use', '=', 'purchase')])
    output_tax = fields.Many2one('account.tax', string='销项税', domain=[('type_tax_use', '=', 'sale')])
    raw_material_code = fields.Char('原材料代码')
    validity_period = fields.Integer('有效期')

    @api.onchange('product_status')
    def _onchange_product_status(self):
        if self.product_status == 'disable':
            self.active = False

    @api.onchange('input_tax')
    def _onchange_input_tax(self):
        if self.input_tax:
            self.supplier_taxes_id = [(5, 0, 0), (4, self.input_tax.id, 0)]

    @api.onchange('output_tax')
    def _onchange_output_tax(self):
        if self.output_tax:
            self.taxes_id = [(5, 0, 0), (4, self.output_tax.id, 0)]

    @api.onchange('trace_back')
    def _onchange_trace_back(self):
        if self.trace_back == 'batch_no':
            self.tracking = 'lot'
        elif self.trace_back == 'no_tracking_info':
            self.tracking = 'none'

    @api.model
    def create(self, vals):
        if vals.get('product_code', '新建') == '新建':
            vals['product_code'] = self.env['ir.sequence'].next_by_code('product.template.num')
        return super(ProductTemplate, self).create(vals)

    @api.depends('categ_id.complete_cls_code', 'product_code')
    def _compute_code(self):
        for rec in self:
            if rec.categ_id.complete_cls_code and rec.product_code:
                rec.complete_product_code = rec.categ_id.complete_cls_code + rec.product_code


