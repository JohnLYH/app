import base64
import re
import xlrd

import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

import_fields_customer = [
    'num_customer',
    'company_id',
    'name',
    'category_customer_id',
    'contact_name',
    'mobile',
    'job_id',
    'sex',
    'state_id',
    'city_id',
    'company_type',
    'device_type',
    'salesman',
    'finance_ids_name',
    'finance_ids_bank',
    'finance_ids_account',
    'finance_address',
    'finance_telephone',
    'finance_contract_name',
    'tax_id',
    'finance_category',
    'payment_id'
]

import_fields_supplier = [
    'num',
    'company_id',
    'name',
    'category_supplier',
    'contact_name',
    'mobile',
    'job_id',
    'sex',
    'state_id',
    'city_id',
    'company_type',
    'salesman',
    'finance_ids_name',
    'finance_ids_bank',
    'finance_ids_account',
    'finance_address',
    'finance_telephone',
    'finance_contract_name',
    'tax_id',
    'finance_category',
    'payment_id'
]

default_fields_list = [
    "company_id",
    "num",
    "num_customer",
    "contact_name",
    "mobile",
    "sex",
    "job_id",
    "email",
    "vat",
    "name",
    "category_customer_id",
    "category_supplier",
    "supplier",
    "customer",
    "company_type",
    "device_type",
    "auth_product_ids",
    "create_date",
    "website",
    "country_id",
    "state_id",
    "city_id",
    "area_id",
    "street",
    "salesman",
    "area_manager",
    "finance_address",
    "tax_id",
    "finance_telephone",
    "category_id",
    "finance_contract_name",
    "payment_id",
    "finance_ids",
    "qualification_ids",
    ]

val_map = {
    '男': 'male',
    '女': 'female',
    '企业': 'company',
    '个人': 'person',
    '增值税专票': 'special_vote',
    '普票': 'general_vote',
    '2类': 'class_two',
    '3类': 'class_three',
    '供应商': 'supplier',
    '物流公司': 'logistics',
    '合作企业': 'enterprise',
}


class CustomerOperationWizard(models.TransientModel):
    _name = 'customer.operation.wizard'

    import_excel = fields.Binary(string='导入客户数据', requried=True)
    is_visible = fields.Boolean('可见', default=True)

    @api.one
    def action_import_customer(self):
        file_contents = base64.decodebytes(self.import_excel)
        # 通过文件内容构造Excel文件对象
        wb = xlrd.open_workbook(file_contents=file_contents)
        sheets = wb.sheets()
        partner_tmpl = self.env['res.partner']
        for sh in sheets:
            start_row = 1
            for row_index in range(start_row, sh.nrows):
                row_values = sh.row_values(row_index)
                values = {}
                finance_dict = {}
                # 判断当前导入的文件是供应商还是客户
                if sh.ncols == 22:
                    import_fields = import_fields_customer
                else:
                    import_fields = import_fields_supplier
                for field, val in zip(import_fields, row_values):
                    if isinstance(val, str):
                        val = val.strip()
                    if field == 'num' and not re.match('^[ABCW]\d{3}$', val):
                        raise UserError('供应商编码不符合要求, 行号[%d]。' % (row_index + 1))
                    if field == 'num_customer' and not re.match('^[a-z]{2}.\d{6}$', val):
                        raise UserError('客户编码不符合要求, 行号[%d]。' % (row_index+1))
                    if field == 'company_id' and self.env['res.company'].search([('name', '=', val)]):
                        val = self.env['res.company'].search([('name', '=', val)]).id
                    if field == 'name' and not val:
                        raise UserError('客户名称未填写, 行号[%d]。' % (row_index + 1))
                    if field == 'category_supplier' and val in val_map.keys():
                        val = val_map[val]
                    # 客户分类
                    if field == 'category_customer_id':
                        if self.env['biote.customer.category'].search([('name', '=', val)]):
                            val = self.env['biote.customer.category'].search([('name', '=', val)]).id
                        else:
                            self.env['biote.customer.category'].create({
                                'name': val
                            })
                            val = self.env['biote.customer.category'].search([('name', '=', val)]).id
                    # 联系人职务
                    if field == 'job_id':
                        if self.env['biote.job'].search([('name', '=', val)]):
                            val = self.env['biote.job'].search([('name', '=', val)]).id
                        else:
                            self.env['biote.job'].create({
                                'name': val
                            })
                            val = self.env['biote.job'].search([('name', '=', val)]).id

                    if field == 'sex' and val in val_map.keys():
                        val = val_map[val]

                    if field == 'state_id' and self.env['res.country.state'].search([('name', '=', val)]):
                        val = self.env['res.country.state'].search([('name', '=', val)]).id
                    if field == 'city_id' and self.env['res.country.city'].search([('name', '=', val)]):
                        val = self.env['res.country.city'].search([('name', '=', val)]).id
                    if field == 'company_type' and val in val_map.keys():
                        val = val_map[val]
                    if field == 'device_type':
                        if val in val_map.keys():
                            val = val_map[val]
                        else:
                            raise UserError('不存在此类机械类型, 行号[%d]。' % (row_index + 1))
                    if field == 'salesman':
                        if self.env['hr.employee'].search([('name', '=', val)]):
                            val = self.env['hr.employee'].search([('name', '=', val)]).id
                        else:
                            raise UserError('请先维护此员工信息, 行号[%d]。' % (row_index + 1))

                    if field == 'finance_ids_name' and val:
                        finance_dict['name'] = val

                    if field == 'finance_ids_bank':
                        if self.env['biote.bank'].search([('name', '=', val)]):
                            finance_dict['bank_name'] = self.env['biote.bank'].search([('name', '=', val)]).id
                        else:
                            self.env['biote.bank'].create({
                                'name': val
                            })
                            finance_dict['bank_name'] = self.env['biote.bank'].search([('name', '=', val)]).id
                    if field == 'finance_ids_account' and val:
                        finance_dict['account_num'] = val
                        tem_dict = {'finance_ids': [(0, 0, finance_dict)]}
                        values.update(tem_dict)

                    if field == 'tax_id':
                        if self.env['account.tax'].search([('amount', '=', val)]):
                            val = self.env['account.tax'].search([('amount', '=', val)]).id
                        else:
                            raise UserError('请先维护开票税率, 行号[%d]。' % (row_index + 1))
                    if field == 'finance_category':
                        if val in val_map.keys():
                            val = val_map[val]
                        else:
                            raise UserError('请先维护开票类型, 行号[%d]。' % (row_index + 1))

                    if field == 'payment_id':
                        if self.env['biote.payment'].search([('name', '=', val)]):
                            val = self.env['biote.payment'].search([('name', '=', val)]).id
                        else:
                            self.env['biote.payment'].create({
                                'name': val
                            })
                            val = self.env['biote.payment'].search([('name', '=', val)]).id
                    if val and field != 'finance_ids_name' and field != 'finance_ids_account' and field != 'finance_ids_bank':
                        values.update({field: val})
                res = partner_tmpl.default_get(default_fields_list)
                if sh.ncols == 21:
                    values.update({
                        'supplier': True,
                        'customer': False,
                    })
                res.update(values)
                partner_tmpl.create(res)
        return True
