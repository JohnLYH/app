import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class OASimpleTest(models.Model):
    _name = 'oa.simple.test'
    _inherit = ['oa.workflow.mixin']
    _description = '工作流测试'

    name = fields.Char(string='名称')
    state = fields.Selection(
        string='状态', 
        selection=[('draft', '草稿'), ('done', '完成'), ('cancel', '取消')]
    )


# 测试ir.model模型的_reflect_model_params方法的调用时机
class OASimpleTest2(models.Model):
    _name = 'oa.simple.test2'
    _inherit = ['oa.workflow.mixin']
    _description = '工作流测试'

    name = fields.Char(string='名称')
    state = fields.Selection(
        string='状态', 
        selection=[('draft', '草稿'), ('done', '完成'), ('cancel', '取消')]
    )
    