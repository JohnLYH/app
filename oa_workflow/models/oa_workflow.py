import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.osv import expression


_logger = logging.getLogger(__name__)


'''
# 约定
* 主工作流暂时只能是串行工作流
* 主工作流中同时只能存在一个子工作流
* 子工作流未完成主流程不能继续
    * 子工作流是串行路线时，状态为done时判定工作流完成
    * 子工作流是并行路线时，parallel_result=approve时判定为完成
* 子工作流可以发起多次，有一次为完成即可继续主流程审批
'''
class OAWorkflow(models.Model):
    _name = 'oa.workflow'
    _description = '审批相关信息'

    result_ids = fields.One2many(
        comodel_name='oa.workflow.result', inverse_name='workflow_id', string='审批结果')
    route_id = fields.Many2one(comodel_name='oa.workflow.route', string='审批路线')
    cur_stage_id = fields.Many2one(comodel_name='oa.workflow.stage', string='当前阶段')
    # 用户创建表单后是draft，如果点击审批则进入progress状态
    state = fields.Selection(
        string='工作流状态', selection=[
            ('draft', '未开始'), ('progress', '进行中'), ('subflow', '子工作流'), ('done', '已完成')
        ],
        default='draft'
    )
    subflow_result = fields.Selection(
        string='子工作流状态', selection=[('ignore', '忽略'), ('approve', '可审批'), ('refused', '退回')], 
        compute='_compute_subflow_result',
        help='当主流的审批阶段可以生成子流时，通过该字段判断阶段是否可审批'
    )
    # 串行通过工作流的done状态来判断是否审批通过
    # 并行工作流，完成后（done）需要根据审批结果计算流程的结果
    parallel_result = fields.Selection(
        string='并行审批结果', selection=[('approve', '通过'), ('refused', '退回')], 
        compute='_compute_parallel_result'
    )
    access_stage = fields.Boolean(string='用户可审批', compute='_compute_access_stage')
    workflow_type = fields.Selection(
        string='工作流类型', selection=[('main', '主流程'), ('sub', '分支流程')], default='main')
    route_type = fields.Selection(related='route_id.route_type')
    stage_id = fields.Many2one(
        comodel_name='oa.workflow.stage', string='子工作流阶段', 
        help='当工作流类型是分支流程时，该字段表示产生该分支流程的阶段'
    )
    parent_id = fields.Many2one(comodel_name='oa.workflow', string='上级工作流')
    child_ids = fields.One2many(comodel_name='oa.workflow', inverse_name='parent_id', string='子工作流')
    cur_subflow_id = fields.Many2one(
        comodel_name='oa.workflow', string='当前子工作流', compute='_compute_cur_subflow_id')
    parallel_remain_stage_ids = fields.Many2many(
        comodel_name='oa.workflow.stage', string='剩余审批阶段', compute='_compute_parallel_stage_ids')
    parallel_access_stage_ids = fields.Many2many(
        comodel_name='oa.workflow.stage', string='可审批阶段', compute='_compute_parallel_stage_ids')
    record = fields.Reference(selection='_reference_models', readonly=True, string='工作流关联记录')                 

    @api.model
    def _reference_models(self):
        return self.env['oa.workflow.route'].search([]).mapped('model_id').mapped(
            lambda r: (r.model, r.name))

    @api.one
    def _compute_subflow_result(self):
        # 使用该结果时主流运行
        if self.cur_stage_id.has_subflow and self.state == 'progress':
            stage_subflow_ids = self.child_ids.filtered(
                lambda r: r.state == 'done' and r.stage_id == self.cur_stage_id)
            # 如果阶段产生过分支审批，需要根据分支审批的结果进行判断
            if stage_subflow_ids:
                if self.cur_stage_id.subflow_type == 'serial':
                    self.subflow_result = 'approve'
                elif self.cur_stage_id.subflow_type == 'parallel':
                    # 所有的并行子流中只要有一个通过，则主流中的阶段可审批
                    if any(stage_subflow_ids.mapped(lambda r: r.parallel_result == 'approve')):
                        self.subflow_result = 'approve'
                    else:
                        self.subflow_result = 'refused'
            else:
                # 忽略分支审批
                # TODO: 为产生分支审批的阶段添加一个标识，判断阶段是否可忽略
                self.subflow_result = 'ignore'

    @api.one
    @api.depends('result_ids')
    def _compute_parallel_stage_ids(self):
        # 这里约定并行审批不会产生子审批
        if self.state == 'progress' and self.route_type == 'parallel':
            done_stage_ids = self.result_ids.mapped('stage_id')
            self.parallel_remain_stage_ids = self.route_id.stage_ids - done_stage_ids
            all_access_stage_ids = self.route_id.stage_ids.filtered(lambda r: r.access_stage)
            self.parallel_access_stage_ids = all_access_stage_ids & self.parallel_remain_stage_ids

    @api.one
    def _compute_parallel_result(self):
        if self.state == 'done' and self.route_type == 'parallel':
            # result模型中的result字段有一个值是subflow, 这里约定并行审批不会产生子审批
            if all(self.result_ids.mapped(lambda r: r.result == 'approve')):
                self.parallel_result = 'approve'
            else:
                self.parallel_result = 'refused'

    @api.one
    def _compute_cur_subflow_id(self):
        # 通过父流与当前阶段来计算当前的子流
        child_id = self.child_ids.filtered(
            lambda r: r.stage_id == self.cur_stage_id and r.state not in ('draft', 'done')
        )
        if len(child_id) > 1:
            raise UserError('审批阶段只能执行一个子工作流！')
        self.cur_subflow_id = child_id

    @api.one
    def _compute_access_stage(self):
        if self.state in ('progress', 'subflow'):
            if self.state == 'subflow':
                # 使用子工作流的判断
                self.access_stage = self.cur_subflow_id.access_stage
            else:
                if self.route_type == 'serial':
                    self.access_stage = self.cur_stage_id.access_stage
                elif self.route_type == 'parallel':
                    # 并行审批不论是同意还是拒绝，只能审批一次，已产生result的stage不参与判断
                    self.access_stage = bool(self.parallel_access_stage_ids)
                    
    @api.multi
    def workflow_execute(self, result, opinion):
        for rec in self:
            if rec.state != 'progress':
                raise UserError('当前工作流不能进行审批，工作流状态[%s]' % rec.state)
            if rec.route_type == 'serial':
                if result == 'approve' and self.cur_stage_id.has_subflow and \
                self.subflow_result == 'refused':
                    raise UserError('发起的工作流审批未通过！')
                # 串行审批时如果点击同意，默认意见就是同意
                if not opinion and result == 'approve':
                    opinion = '同意'
                self.env['oa.workflow.result'].generate_workflow_result(
                    result, opinion, rec.cur_stage_id.id, rec.id)
                if result == 'approve':
                    if rec.cur_stage_id.is_end_stage:
                        rec.state = 'done'
                        rec.cur_stage_id = False
                        # 工作流完成后调用审批记录的回调
                        if getattr(rec.record, 'workflow_done_callback', False):
                            rec.record.workflow_done_callback()
                    else:
                        next_stage = rec.route_id.get_next_stage(rec.cur_stage_id, rec.record)
                        rec.cur_stage_id = next_stage.id
                elif result == 'refused':
                    # 流程中只要有一人退回则审批回到提交前状态
                    rec.state = 'draft'
                    rec.cur_stage_id = False
                    # if rec.cur_stage_id.is_start_stage:
                    #     rec.state = 'draft'
                    #     rec.cur_stage_id = False
                    # else:
                    #     pre_stage = rec.route_id.get_pre_stage(rec.cur_stage_id)
                    #     rec.cur_stage_id = pre_stage.id
            elif rec.route_type == 'parallel':
                for s in self.parallel_access_stage_ids:
                    # parallel_remain_stage_ids受result_ids影响，在同一个事务中取值时会从缓存中取值
                    self.env['oa.workflow.result'].generate_workflow_result(
                    result, opinion, s.id, rec.id)
                # 并行审批每次执行审批后需要判断工作流是否执行结束
                if not rec.parallel_remain_stage_ids:
                    rec.state = 'done'
            # 如果工作流已完成并且是子流，需要将父工作流的状态改变为progress, 影响主流的access_stage判断
            if rec.state == 'done' and rec.workflow_type == 'sub':
                rec.parent_id.state = 'progress'

    def _get_route_id(self):
        # 每次开始审批时都会根据工作流关联记录的状态获取对应的路线
        model_name = self.record._name
        valid_routes = self.env['oa.workflow.route'].search([('model_name', '=', model_name)])
        domain_routes = valid_routes.filtered(lambda r: safe_eval(r.domain))
        if domain_routes:
            for route in domain_routes.sorted(lambda r: r.sequence):
                search_domain = expression.AND([
                    safe_eval(route.domain), [('id', '=', self.record.id)]])
                if self.env[model_name].search_count(search_domain):
                    return route
        routes = valid_routes - domain_routes
        if not routes:
            raise ValidationError('未找到单据的审批路线！')
        return routes.sorted(lambda r: r.sequence)[0]
                            
    @api.multi
    def start_workflow(self):
        for rec in self:
            route_id = self._get_route_id()
            # 对工作流路线的合法性进行校验
            route_id.check_stage_ids()
            rec.route_id = route_id
            rec.cur_stage_id = rec.route_id.get_first_stage()
            rec.state = 'progress'

    @api.multi
    def start_subflow(self, opinion, subflow):
        self.ensure_one()
        self.state = 'subflow'
        self.env['oa.workflow.result'].generate_workflow_result(
            'subflow', opinion, self.cur_stage_id.id, self.id, subflow.id)