import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class OAWorkflowMixin(models.AbstractModel):
    _name = 'oa.workflow.mixin'
    _description = '其他模型使用工作流'

    # mixin类需要注意变量与方法的命名，保证不与其他类的命名冲突
    # @api.model
    # def _wf_get_stages_selection(self):
    #     route_id = self._wf_get_route_id()
    #     sorted_stages = route_id.stage_ids.sorted(lambda r: r.sequence)
    #     return sorted_stages.mapped(lambda r: (r.id, r.name))

    # wf_stage = fields.Selection(
    #     string='审批阶段', selection=_wf_get_stages_selection, compute='_compute_wf_stage')
    
    workflow_id = fields.Many2one(comodel_name='oa.workflow', string='工作流')
    # 这里设置为readonly是防止单据保存时将workflow的state设置为空
    workflow_state = fields.Selection(related='workflow_id.state', readonly=True)
    access_stage = fields.Boolean(
        related='workflow_id.access_stage', readonly=True, related_sudo=False)
    workflow_result_ids = fields.One2many(related='workflow_id.result_ids', readonly=True)
    has_subflow = fields.Boolean(related='cur_stage_id.has_subflow', readonly=True) 
    show_subflow_btn = fields.Boolean(string='显示子审批按钮', compute='_compute_show_subflow_btn')
    cur_stage_id = fields.Many2one(related='workflow_id.cur_stage_id')
    valid_stage_ids = fields.One2many(
        comodel_name='oa.workflow.stage', string='有效审批阶段', compute='_compute_valid_stage_ids')
    history_workflows = fields.Char(string='历史工作流', help='技术字段，用于存储历史工作流字符串形式的id列表')
    history_workflow_ids = fields.One2many(
        comodel_name='oa.workflow', string='历史工作流', compute='_compute_history_workflow_ids')

    def _compute_history_workflow_ids(self):
        # 将history_workflows存储的id字符串转换为Python列表赋值给history_workflow_ids字段
        pass

    def _compute_valid_stage_ids(self):
        for r in self:
            r.valid_stage_ids = self.workflow_id.route_id.get_record_valid_stages(r)

    @api.one
    def _compute_show_subflow_btn(self):
        if self.has_subflow:
            if self.workflow_state == 'subflow':
                self.show_subflow_btn = False
            else:
                if self.workflow_id.subflow_result == 'approve':
                    # 子工作流审批通过无需再显示按钮
                    self.show_subflow_btn = False
                else:
                    if self.access_stage:
                        self.show_subflow_btn = True
        else:
            self.show_subflow_btn = False

    @api.model
    def create(self, vals):
        # 先查询当前模型是否有审批路线
        if self.env['oa.workflow.route'].search_count([('model_name', '=', self._name)]):
            wf = self.env['oa.workflow'].create({})
            vals.update(workflow_id=wf.id)
            rec = super(OAWorkflowMixin, self).create(vals)
            wf.record = self._name + ',' + str(rec.id)       
            return rec
        return super(OAWorkflowMixin, self).create(vals)

    def _wf_get_opinion_action(self, result):
        default_workflow_id = self.workflow_id
        if self.workflow_state == 'subflow':
            default_workflow_id = self.workflow_id.cur_subflow_id
        action = {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'name': '审批意见',
            'res_model': 'oa.workflow.opinion.wiz',
            'context': {'default_result': result, 'default_workflow_id': default_workflow_id.id},
            'target': 'new'
        }
        return action

    def _wf_get_subflow_action(self):
        action = {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'name': '自定义子工作流',
            'res_model': 'oa.subflow.wiz',
            'context': {
                'default_cur_stage_id': self.cur_stage_id.id,
                'default_workflow_id': self.workflow_id.id
            },
            'target': 'new'
        }
        return action

    @api.multi
    def btn_workflow_approve(self):
        self.ensure_one()
        return self._wf_get_opinion_action('approve')

    @api.multi
    def btn_workflow_refused(self):
        self.ensure_one()
        return self._wf_get_opinion_action('refused')

    @api.multi
    def btn_start_subflow(self):
        self.ensure_one()
        return self._wf_get_subflow_action()

    @api.multi
    def start_workflow(self):
        for rec in self:
            rec.workflow_id.start_workflow()
