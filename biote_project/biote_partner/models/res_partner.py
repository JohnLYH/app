import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)
SUPPLIER_NUM = ['A', 'B', 'C', 'W']


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # 基本信息
    num = fields.Char(string='供应商编码', size=4)
    num_customer = fields.Char(string='客户编码')
    category_supplier = fields.Selection([
        ('supplier', '供应商'),
        ('logistics', '物流公司'),
        ('enterprise', '合作企业')
        ], string='供应商分类')
    category_customer_id = fields.Many2one('biote.customer.category', string='客户分类', default='')
    # 联系人信息 联系人，性别，电话mobile，职务多对一，
    contact_name = fields.Char(string='联系人')
    sex = fields.Selection([('male', '男'), ('female', '女')], string='性别')
    job_id = fields.Many2one('biote.job', string='职务')
    # 客户相关信息
    # auth_product_ids = fields.One2many('product.product', string='授权产品')
    # service_hospital = fields.Char(string='服务医院')
    auth_type = fields.Selection([
        ('dev_auth', '开发授权'),
        ('sale_auth', '销售授权'),
        ('stop_auth', '终止授权')], string='授权书类型')
    # auth_end_date = fields.Date(string='授权截止时间')
    area_manager_id = fields.Many2one('hr.employee', string='区域经理')
    salesman_id = fields.Many2one('hr.employee', string='业务员')
    device_type = fields.Selection([('class_two', '2类'), ('class_three', '3类')], string='器械类别')
    # 资质证书
    qualification_ids = fields.One2many('biote.qualification.document', 'partner_id', string='资质证书')
    city_id = fields.Many2one('res.country.city', string='城市')
    area_id = fields.Many2one('res.country.area', string='区')
    # 财务信息
    finance_ids = fields.One2many('biote.partner.finance', 'partner_id', string='财务信息')
    finance_address = fields.Char(string='开票地址')
    finance_telephone = fields.Char(string='财务电话')
    finance_contract_name = fields.Char(string='财务联系人')
    tax_id = fields.Many2one('account.tax', string='开票税率')
    finance_category = fields.Selection([('special_vote', '增值税专票'), ('general_vote', '普票')], string='开票类型')
    payment_id = fields.Many2one('biote.payment', string='付款方式')

    _sql_constraints = [
        ('num_unique',
         'UNIQUE(num)',
         "供应商编码必须唯一！"),
    ]

    def _check_num_first(self):
        if self.supplier:
            if self.num:
                if len(self.num) == 4:
                    num_first = self.num[0]
                    if num_first in SUPPLIER_NUM:
                        ret = self.search([('num', 'like', num_first), ('num', '!=', self.num)],
                                          order='num DESC', offset=0, limit=1)
                        if ret:
                            max_num = int(ret.num[1:]) + 1
                            tem_num = int(self.num[1:])
                            if tem_num != max_num:
                                raise UserError('下一个编号为%d' % max_num)
                    else:
                        raise ValidationError("供应商编码需以A或B或C或W开头！")
                else:
                    raise ValidationError("供应商编码长度为4位数！")

    @api.constrains('num')
    def _check_num(self):
        if self.customer and self.supplier:
            if not self.num:
                raise ValidationError("供应商编码不能为空！")
            self._check_num_first()

    @api.onchange('num')
    def _onchange_num(self):
        self._check_num_first()

    @api.onchange('state_id')
    def _onchange_state_id(self):
        self.city_id = False
        if self.state_id:
            return {'domain': {'city_id': [('state_id', '=', self.state_id.id)]}}
        else:
            return {'domain': {'city_id': []}}

    @api.onchange('city_id')
    def _onchange_city_id(self):
        self.area_id = False
        if self.city_id:
            return {'domain': {'area_id': [('city_id', '=', self.city_id.id)]}}
        else:
            return {'domain': {'area_id': []}}

    @api.model
    def create(self, vals):
        if vals.get('category_customer_id'):
            temp = self.env['biote.customer.category'].browse(vals['category_customer_id']).name
            categ_map = {
                '院': 'customer.category.yx',
                'o': 'customer.category.otc',
                '其': 'customer.category.qt',
            }
            for r in ['院', 'o', '其']:
                if temp.startswith(r):
                    vals['num_customer'] = self.env['ir.sequence'].next_by_code(categ_map.get(r))
        return super(ResPartner, self).create(vals)


class BioteJob(models.Model):
    _name = 'biote.job'
    _description = '合作伙伴职务模型'

    name = fields.Char(string='职务名称')


class BiotePayment(models.Model):
    _name = 'biote.payment'
    _description = '付款方式'

    name = fields.Char(string='付款方式')
