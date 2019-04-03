from datetime import datetime, timedelta
import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class BioteQualificationDocument(models.Model):
    _name = 'biote.qualification.document'
    _description = '资质文件模型'

    name = fields.Char(string='文件名称')
    partner_id = fields.Many2one('res.partner', string='所属企业')
    category = fields.Selection([
        ('lic', '营业执照'),
        ('tax_reg', '税务登记证'),
        ('org_code', '组织机构代码'),
        ('business_pemit_3', '3类经营许可'),
        ('business_lic_3', '3类营业执照'),
        ('qa_protocol_3', '3类质保协议')
        ], string='资质文件类型', requried=True)
    # 该字段为展示文件的名称，当下载文件，或展示文件时使用的名称
    fname = fields.Char(string='文件名称')
    data = fields.Binary(string='资质文件')
    start_date = fields.Date(string='开始日期', default=fields.Date.today)
    end_date = fields.Date(string='结束日期', default=fields.Date.today)
    lead_time = fields.Integer(string='预警提前期', default='30')
    # 预警时间=结束日期-提前期
    warning_time = fields.Date(string='预警时间', compute='_compute_warning_time_date')
    state = fields.Selection([('normal', '正常'), ('warning', '预警期'), ('delay', '超期')],
                             default='normal', string='资质状态', compute='_compute_state', store=False)
    code = fields.Char(string='资质编号')
    is_customer = fields.Boolean(string='客户')
    is_supplier = fields.Boolean(string='供应商')
    note = fields.Text(string='备注')

    _sql_constraints = [
        ('code_unique',
         'UNIQUE(code)',
         "证书编号必须唯一"),
    ]

    @api.depends('end_date', 'lead_time')
    def _compute_warning_time_date(self):
        for r in self:
            # 把字符串转换成时间对象
            end_date = datetime.strptime(r.end_date, '%Y-%m-%d')
            lead_time = timedelta(days=r.lead_time)
            r.warning_time = end_date - lead_time

    @api.depends('warning_time', 'lead_time')
    def _compute_state(self):
        for r in self:
            today = datetime.now()
            warning_time = datetime.strptime(r.warning_time, '%Y-%m-%d')
            # print(warning_time) 2019-01-02 00:00:00
            end_date = datetime.strptime(r.end_date, '%Y-%m-%d')
            if today < warning_time:
                r.state = 'normal'
            elif warning_time < today < end_date:
                r.state = 'warning'
            else:
                r.state = 'delay'

