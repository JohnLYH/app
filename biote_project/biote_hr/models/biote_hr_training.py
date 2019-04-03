from odoo import models, fields, api


class BioteBioteHrTraining(models.Model):
    _name = 'biote.hr.training'
    _order = 'start_date DESC'

    start_date = fields.Date(string="开始日期", required=True)
    end_date = fields.Date(string="结束日期", required=True)
    institution = fields.Char(string="培训机构", required=True)
    course = fields.Char(string="培训课程", required=True)
    certificate = fields.Selection([("1", "毕业"), ("2", "结业"), ("3", "资格证")], string="证书")
    employee_id = fields.Many2one("hr.employee", string="所属人员")
