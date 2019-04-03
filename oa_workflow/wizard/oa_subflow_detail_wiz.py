import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class OASubflowDetail(models.TransientModel):
    _name = 'oa.subflow.detail.wiz'
    _description = '子工作流审批详情'

    subflow_id = fields.Many2one(comodel_name='oa.workflow', string='工作流')
    subflow_result_ids = fields.One2many(related='subflow_id.result_ids')
    subflow_stage_ids = fields.One2many(related='subflow_id.route_id.stage_ids')
    