import logging

from odoo import models, fields, api, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class OAWorkflowStage(models.Model):
    _name = 'oa.workflow.stage'
    _description = '审批阶段'
    _order = "sequence,id"

    name = fields.Char(string='阶段名称', required=True)
    route_id = fields.Many2one(comodel_name='oa.workflow.route', string='工作流路线')
    model_name = fields.Char(related='route_id.model_name')
    
    has_subflow = fields.Boolean(string='有子审批', default=False)
    subflow_type = fields.Selection(
        string='子审批类型', selection=[('parallel', '并行'), ('serial', '串行')], default='parallel'
    )
    # 固定路线中时所有记录共享，因此不能用来存储子流
    # subflow_id = fields.Many2one(comodel_name='oa.workflow', string='子工作流')
    sequence = fields.Integer(
        string='审批顺序', help='默认根据该值获取阶段的前后阶段')
    #TODO: next_stage_id pre_stage_id 如果指定则优先使用这两个值
    department_ids = fields.Many2many(comodel_name='hr.department', string='审批部门')
    department_stage_type = fields.Selection(
        string='部门审批类型', selection=[('all', '全部人员'), ('manager', '部门主管')], default='all',
        help='部门审批时会通过该值判断审批人员'
    )
    stage_employee_ids = fields.Many2many(
        comodel_name='hr.employee', string='审批用户', help='判断审批权限时，优先查找指定用户，然后查找部门')
    access_stage = fields.Boolean(string='阶段可审批', compute='_compute_access_stage')
    is_end_stage = fields.Boolean(string='结束阶段', compute='_compute_stage_position')
    is_start_stage = fields.Boolean(string='开始阶段', compute='_compute_stage_position')
    domain = fields.Char(string="过滤条件", default=[])

    # @api.depends('sequence', 'route_id.stage_ids')
    def _compute_stage_position(self):
        # TODO: 可以进行优化
        for stage in self:
            seqs = stage.route_id.get_stage_sequences()
            stage.is_start_stage = (stage.sequence == seqs[0])
            stage.is_end_stage = (stage.sequence == seqs[-1])

    @api.onchange('sequence')
    def _onchange_sequence(self):
        if not self.sequence:
            seqs = self.route_id.get_stage_sequences()
            self.sequence = (seqs[-1] + 1) if seqs else 1

    # 根据当前访问用户来判断是否可以审批单据
    @api.one
    def _compute_access_stage(self):
        if self.env.uid == SUPERUSER_ID:
            has_access = True
        else:
            has_access = self.env.user & self.stage_employee_ids.mapped('user_id')
            if not has_access and self.department_ids:
                # TODO: 上级部门与下级部门
                manager_ids = self.department_ids.mapped('manager_id.user_id')
                member_ids = self.department_ids.mapped('member_ids').mapped('user_id')
                if self.department_stage_type == 'all':
                    has_access = self.env.user & (manager_ids | member_ids)
                elif self.department_stage_type == 'manager':
                    has_access = self.env.user & manager_ids
        self.access_stage = has_access
