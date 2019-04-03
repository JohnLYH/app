import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class OASubflowWiz(models.TransientModel):
    _name = 'oa.subflow.wiz'
    _description = '创建自定义子工作流'

    employee_ids = fields.Many2many(
        comodel_name='hr.employee', string='审批人', required=True, domain=[('user_id', '!=', False)])
    workflow_id = fields.Many2one(comodel_name='oa.workflow', string='工作流')
    cur_stage_id = fields.Many2one(comodel_name='oa.workflow.stage', string='当前审批阶段')
    opinion = fields.Text(string='审批意见')

    @api.multi
    def btn_generate_subflow(self):
        route_vals = {
            'name': '[%s]自定义子工作流路线' % self.cur_stage_id.name,
            'route_type': 'parallel',
            'is_custom': True
        }
        route = self.env['oa.workflow.route'].create(route_vals)
        for employee_id in self.employee_ids:
            stage_vals = {
                'name': '[%s]审批' % employee_id.name,
                'route_id': route.id,
                'stage_employee_ids': [(4, employee_id.id, False)]
            }
            self.env['oa.workflow.stage'].create(stage_vals)
        subflow_vals = {
            'route_id': route.id,
            'workflow_type': 'sub',
            'stage_id': self.cur_stage_id.id,
            'parent_id': self.workflow_id.id,
            # 子工作流产生后状态是进行中
            'state': 'progress'
        }
        subflow = self.env['oa.workflow'].create(subflow_vals)
        # 产生分支工作流后，改变主工作流的状态
        self.workflow_id.start_subflow(self.opinion, subflow)
