from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from datetime import datetime


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    complete_num = fields.Char(string="计算编码", compute="_compute_complete_num")
    trial_start_date = fields.Date(string="试用期开始日期")
    hire_date = fields.Date(string="入职日期")
    trial_type = fields.Selection([
        ("1", "1个月"), ("2", "2个月"), ("3", "3个月"),
        ("4", "4个月"), ("5", "5个月"), ("6", "6个月"),
        ("0", "自定义日期")], string="试用期", default="3")
    trial_length = fields.Integer(string="试用期时长")
    trial_end_date = fields.Date(string="试用期结束日期")
    service_length = fields.Integer(string="工龄", compute='_compute_service_length', store=True)
    lead_time_type = fields.Selection([
        ("0", "自定义日期"),
        ("5", "提前5天"),
        ("10", "提前10天"),
        ("15", "提前15天"),
    ], string="转正提醒日期")
    trial_notify_time = fields.Date(string="转正提醒日期")
    trial_date = fields.Date(string="转正日期")
    political_status = fields.Selection(
        [("0", "群众"), ("1", "中共党员"), ("2", "中共预备党员"), ("3", "共青团员"),
         ("4", "民革党员"), ("5", "民盟盟员"), ("6", "民建会员"), ("7", "民进会员"),
         ("8", "农工党党员"), ("9", "致公党党员"), ("10", "九三学社社员"), ("11", "台盟盟员"),
         ("12", "无党派人士")], string="政治面貌")
    native_place_type = fields.Selection([("0", "非农业户口"), ("1", "农业户口")], string="户籍性质")
    degree = fields.Selection([
        ("0", "小学"), ("1", "初中"), ("2", "高中"), ("3", "中专"),
        ("4", "职校"), ("5", "中技"), ("6", "专科"), ("7", "本科"),
        ("8", "硕士"), ("9", "博士"), ("10", "无")], string="最高学历")
    native_place = fields.Char(string="籍贯")
    city = fields.Char(string="城市")
    ethnic = fields.Char(string="民族")
    job_title = fields.Selection([
        ("senior", "高级"), ("intermediate", "中级"), ("junior", "初级"), ("normal", "无")
    ])
    is_criminal = fields.Boolean(string="是否有犯罪记录")
    criminal_record = fields.Char(string="犯罪记录")
    is_medical = fields.Boolean(string="曾患何种疾病")
    medical_history = fields.Char(string="疾病记录")
    emergency_contact = fields.Char(string="紧急联系人")
    kinship = fields.Char(string="与紧急联系人关系")
    emergency_tel = fields.Char(string="紧急联系人电话")
    residence_address = fields.Char(string="户籍地址")
    address_home = fields.Char(string="现住址")
    residence_zip_code = fields.Char(string="户籍邮编")
    residence_tel = fields.Char(string="户籍固定电话")
    home_zip_code = fields.Char(string="现居地址邮编")
    home_tel = fields.Char(string="现住址固定电话")
    education_ids = fields.One2many("biote.hr.education", "employee_id", string="教育经历")
    training_ids = fields.One2many("biote.hr.training", "employee_id", string="培训经历")
    work_exp_ids = fields.One2many("biote.hr.work.exp", "employee_id", string="工作履历")
    family_ids = fields.One2many("biote.hr.family", "employee_id", string="直系亲属情况")

    @api.onchange("trial_start_date", "trial_type", "trial_length")
    def _onchange_trial_end_date(self):
        if self.trial_type != "0":
            self.trial_length = int(self.trial_type)
        if self.trial_start_date:
            local_trial_length = relativedelta(months=+self.trial_length)
            local_trial_start_date = datetime.strptime(self.trial_start_date, "%Y-%m-%d").date()
            self.trial_end_date = local_trial_length + local_trial_start_date

    @api.onchange('trial_date', 'lead_time_type')
    def _onchange_trial_notify_time(self):
        if self.trial_date:
            tmp_lead_length = relativedelta(days=-int(self.lead_time_type))
            tmp_trial_date = datetime.strptime(self.trial_date, "%Y-%m-%d").date()
            self.trial_notify_time = tmp_lead_length + tmp_trial_date

    @api.onchange('is_criminal')
    def _onchange_criminal_record(self):
        if not self.is_criminal:
            self.criminal_record = None

    @api.onchange('is_medical')
    def _onchange_medical_history(self):
        if not self.is_medical:
            self.medical_history = None

    def _create_user(self, name, login):
        res_users = self.env['res.users']
        values = {
            'login': login,
            'name': name,
            'groups_id': [(4, self.env.ref('base.group_user').id)],
        }
        new_user = res_users.sudo().create(values)
        new_user._set_password(login)
        return new_user

    @api.model
    def create(self, vals):
        num = self.env['ir.sequence'].next_by_code('hr.employee.num') or '/'
        new_user = self._create_user(vals.get('name'), num)
        vals['user_id'] = new_user.id
        vals['permit_no'] = num
        return super(HrEmployee, self).create(vals)

    @api.depends('hire_date')
    def _compute_service_length(self):
        for record in self:
            if record.hire_date:
                tmp_today = fields.Date.from_string(fields.Date.today())
                tmp_hire_date = fields.Date.from_string(record.hire_date)
                record.service_length = int((tmp_today - tmp_hire_date) / timedelta(days=365))

    @api.depends('permit_no', 'department_id')
    def _compute_complete_num(self):
        for record in self:
            if record.permit_no and record.department_id:
                record.complete_num = record.department_id.num + record.permit_no
