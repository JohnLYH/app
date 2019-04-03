import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class OAWorkflowOpinionWiz(models.TransientModel):
    _name = 'oa.workflow.opinion.wiz'
    _description = '审批意见填写框'

    workflow_id = fields.Many2one(comodel_name='oa.workflow', string='工作流')
    result = fields.Selection(string='审批结果', selection=[('approve', '同意'), ('refused', '拒绝')])
    opinion = fields.Text(string='审批意见')
    workflow_type = fields.Selection(related='workflow_id.workflow_type')

    @api.multi
    def workflow_excute(self):
        self.ensure_one()
        workflow_id = self.workflow_id
        if self.workflow_id.state == 'subflow':
            workflow_id = self.workflow_id.cur_subflow_id
        workflow_id.workflow_execute(self.result, self.opinion)
