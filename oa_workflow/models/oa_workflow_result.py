import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class OAWorkflowResult(models.Model):
    _name = 'oa.workflow.result'
    _description = '工作流审批结果'

    name = fields.Char(related='stage_id.name')
    opinion = fields.Char(string='审批意见', required=True)
    result = fields.Selection(
        string='审批结果', required=True,
        selection=[('approve', '同意'), ('refused', '退回'), ('subflow', '子审批')],
    )
    operate_user_id = fields.Many2one(comodel_name='res.users', string='审批人')
    stage_id = fields.Many2one(comodel_name='oa.workflow.stage', string='审批阶段', required=True)
    workflow_id = fields.Many2one(comodel_name='oa.workflow', string='工作流', required=True)
    subflow_id = fields.Many2one(comodel_name='oa.workflow', string='子工作流')
    
    def generate_workflow_result(
        self, result, opinion, stage_id, workflow_id, subflow_id=False):
        vals = {
            'stage_id': stage_id,
            'workflow_id': workflow_id,
            'opinion': opinion,
            'result': result,
            'operate_user_id': self.env.uid,
            'subflow_id': subflow_id
        }
        self.create(vals)

    def action_show_details(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'name': '子审批',
            'res_model': 'oa.subflow.detail.wiz',
            'context': {'default_subflow_id': self.subflow_id.id},
            'target': 'new'
        }
        return action
        