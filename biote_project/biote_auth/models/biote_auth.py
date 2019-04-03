from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class BioteAuth(models.Model):
    _name = 'biote.auth'
    _description = '授权书模型'

    num = fields.Char(string='授权书编号', default=lambda self: '新建')
    category = fields.Selection([
        ('dev_auth', '开发授权'),
        ('sale_auth', '销售授权'),
        ('stop_auth', '终止授权'),
    ], string='申请授权类型', default='dev_auth')
    enterprise_id = fields.Many2one('res.partner', string='被授权企业')
    enterprise_qa = fields.One2many(related='enterprise_id.qualification_ids', string='企业资质')
    hospital_id = fields.Many2one('res.partner', string='授权医院')
    product_id = fields.Many2one('product.product', string='授权产品')
    country_id = fields.Many2one('res.country', string='国家')
    state_id = fields.Many2one('res.country.state', string='省份')
    city_id = fields.Many2one('res.country.city', string='城市')
    area_id = fields.Many2one('res.country.area', string='区')
    predict_sales = fields.Char(string='预估销量')
    applicant_id = fields.Many2one('hr.employee', string='申请人')
    leader_id = fields.Many2one('hr.employee', string='分管领导')
    contract_name = fields.Char(string='联系人')
    phone = fields.Char(string='联系电话')
    recipient = fields.Char(string='收件单位')
    address = fields.Char(string='邮寄地址')
    applicant_date = fields.Date(string='申请日期', default=fields.Date.today)
    auth_date = fields.Selection([
        ('1', '1个月'),
        ('2', '2个月'),
        ('3', '3个月'),
        ('4', '到自然年年底'),
        ('customer_date', '自定义时间'),
    ], string='授权时间段')
    customer_date = fields.Integer(string='自定义时间')
    start_date = fields.Date(string='授权开始日期', required=True)
    end_date = fields.Date(string='结束日期')
    original_num = fields.Char(string='原授权书编号')
    advance_stop_date = fields.Char(string='授权提前终止时间')
    original_start_date = fields.Date(string='原授权开始时间')
    original_end_date = fields.Date(string='原授权结束时间')
    note = fields.Text(string='备注')

    @api.model
    def create(self, vals):
        if vals.get('num', '新建') == '新建':
            vals['num'] = self.env['ir.sequence'].next_by_code(vals['category'].replace('_', '.'))
        return super(BioteAuth, self).create(vals)

    @api.onchange('auth_date', 'start_date', 'customer_date')
    def _onchange_end_date(self):
        if self.start_date:
            start_date = datetime.strptime(self.start_date, '%Y-%m-%d').date()
            if self.auth_date in ['1', '2', '3']:
                auth_date = relativedelta(months=+int(self.auth_date))
                self.end_date = auth_date + start_date
            elif self.auth_date == '4':
                temp_date = self.start_date[0:4]
                self.end_date = temp_date + '-12-31'
            else:
                customer_date = relativedelta(months=+self.customer_date)
                self.end_date = customer_date + start_date

    @api.multi
    def btn_report(self):
        return {
            "name": '预览报表',
            "type": "ir.actions.act_url",
            "url": "/report/pdf/biote_auth.auth_templates/%d" % self.id,
            "target": "new",
        }

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
