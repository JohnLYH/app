from odoo import models, fields, api


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    num = fields.Char(string="部门编码", default='新建')
    department_type = fields.Selection([
        ("management", "管理部门"), ("warehousing", "仓储中心"), ("Purchasing", "采购"),
        ("sales", "销售"), ("Production", "生产中心")], string="部门属性")
    status = fields.Selection([('enable', '启用'), ('disable', '禁用')], default='enable', string="状态")

    @api.model
    def create(self, vals):
        if vals.get('num', '新建') == '新建':
            vals['num'] = self.env['ir.sequence'].next_by_code('hr.department.num') or '/'
        return super(HrDepartment, self).create(vals)

    @api.onchange('status')
    def _onchange_status(self):
        if self.status == 'disable':
            self.active = False
        if self.status == 'enable':
            self.active = True
