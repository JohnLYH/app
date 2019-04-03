import base64
import re
import xlrd

import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


default_fields_list = [
    "image_medium",
    "name",
    "sale_ok",
    "purchase_ok",
    "categ_id",
    "default_code",
    "specification",
    "uom_id",
    "uom_po_id",
    "lot_qty",
    "lot_available_qty",
    "product_eval",
    "lot_reserved_qty",
    "lot_valuation",
    "lot_valuation_tax",
    "description_purchase",
    "description_sale"
]

import_fields = [
    'name',
    'categ_id',
    'default_code',
    'specification'
]


class ProductWizard(models.TransientModel):
    _name = 'rs.product.wizard'

    import_excel = fields.Binary(string='导入产品数据', required=False)

    @api.one
    def action_import_product(self):
        if not self.import_excel:
            raise UserError('请导入要上传的文件!')
        file_contents = base64.decodebytes(self.import_excel)
        wb = xlrd.open_workbook(file_contents=file_contents)
        sheets = wb.sheets()
        product_obj = self.env['product.template']
        category_obj = self.env['product.category']
        for sh in sheets:
            start_row = 1
            for row_index in range(start_row, sh.nrows):
                row_values = sh.row_values(row_index)
                values = {}
                for field, val in zip(import_fields, row_values):
                    if isinstance(val, str):
                        val = val.strip()
                    if field == 'name' and val:
                        if product_obj.search([('name', '=', val)]):
                            raise UserError('产品名称已存在, 行号[%d]。' % (row_index + 1))
                    if field == 'categ_id' and val:
                        if category_obj.search([('name', '=', val)]):
                            val = category_obj.search([('name', '=', val)]).id
                        else:
                            category_obj.create({
                                'name': val
                            })
                            val = category_obj.search([('name', '=', val)]).id
                    if val:
                        values.update({field: val})
                res = product_obj.default_get(default_fields_list)
                res.update(values)
                product_obj.create(res)
        return True
