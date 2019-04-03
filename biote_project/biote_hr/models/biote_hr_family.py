from odoo import models, fields, api


class BioteHrFamily(models.Model):
    _name = 'biote.hr.family'

    name = fields.Char(string="姓名", required=True)
    kinship = fields.Char(string="关系", required=True)
    company = fields.Char(string="工作单位")
    identification_id = fields.Char(string="身份证号")
    home_address = fields.Char(string="家庭住址")
    phone = fields.Char(string="联系电话", required=True)
    employee_id = fields.Many2one("hr.employee", string="所属人员")
