from odoo import models, fields, api


class BioteHrEducation(models.Model):
    _name = 'biote.hr.education'
    _order = 'start_date DESC'

    start_date = fields.Date(string="开始日期", required=True)
    end_date = fields.Date(string="结束日期", required=True)
    school = fields.Char(string="学校", required=True)
    major = fields.Char(string="专业")
    full_time_school = fields.Selection([("1", "全日制"), ("2", "非全日制")], required=True)
    degree = fields.Selection([
        ("0", "小学"), ("1", "初中"), ("2", "高中"), ("3", "中专"),
        ("4", "职校"), ("5", "中技"), ("6", "专科"), ("7", "本科"),
        ("8", "硕士"), ("9", "博士")], string="学历/学位", required=True)
    employee_id = fields.Many2one('hr.employee', string="所属人员")
