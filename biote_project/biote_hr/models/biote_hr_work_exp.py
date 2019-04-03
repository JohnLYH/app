from odoo import models, fields, api


class BioteBioteHrWorkExp(models.Model):
    _name = 'biote.hr.work.exp'
    _order = 'start_date DESC'

    start_date = fields.Date(string="开始日期", required=True)
    end_date = fields.Date(string="结束日期", required=True)
    company = fields.Char(string="就职单位", required=True)
    department = fields.Char(string="部门", required=True)
    job_title = fields.Char(string="职位", required=True)
    certifier = fields.Char(string="证明人", required=True)
    certifier_tel = fields.Char(string="联系电话", required=True)
    employee_id = fields.Many2one("hr.employee", string="所属人员")
