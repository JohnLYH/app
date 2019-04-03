import logging

from odoo import models, fields, api
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


# 约定：串行路线的开始与结束阶段只有一个
class OAWorkflowRoute(models.Model):
    _name = 'oa.workflow.route'
    _description = '工作流路线'
    _order = "sequence,id"

    name = fields.Char(string='路线名称')
    model_name = fields.Char(
        string='模型名称', help='技术字段，通过xml创建路线时通过该字段的值查找ir.model记录')
    model_id = fields.Many2one(
        comodel_name='ir.model',
        string='关联模型',
        domain=[('is_workflow', '=', True)]
    )
    stage_ids = fields.One2many(
        comodel_name='oa.workflow.stage', inverse_name='route_id', string='审批阶段', required=True)
    sequence = fields.Integer(string='路线优先级', help='模型查找路线时sequence值越小，优先级越高')
    route_type = fields.Selection(
        string='路线类型', selection=[('parallel', '并行路线'), ('serial', '串行路线')], default='serial')
    is_custom = fields.Boolean(string='自定义路线', default=False)
    # 过滤条件优先于sequence
    domain = fields.Char(string='路线过滤', help='根据该字段的值与记录id进行过滤获取路线', default='[]')

    @api.onchange('model_id')
    def _onchange_model_id(self):
        self.model_name = self.model_id.model

    # def _inverse_model_id(self):
    #     for rec in self:
    #         rec.model_name = rec.model_id.name

    # @api.depends('model_name')
    # def _compute_model_id(self):
    #     # 由于model_id的获取依赖于model_name，因此通过界面创建route时必须通过onchange获取model_id关联的model_name
    #     if self.model_name:
    #         for rec in self:
    #             model = self.env['ir.model'].search([('model', '=', rec.model_name)])
    #             if not model:
    #                 raise ValidationError('未找到路线关联的模型')
    #             rec.model_id = model.id

    def get_stage_sequences(self):
        self.ensure_one()
        return self.stage_ids.sorted('sequence').mapped('sequence')

    @api.model
    def create(self, vals):
        # 通过xml创建路线不使用model_id
        # 通过界面创建不操作model_name
        if not vals.get('is_custom') and 'model_id' not in vals:
            model_name = vals.get('model_name')
            if not model_name:
                raise ValidationError('没有提供关联模型的信息')
            model = self.env['ir.model'].search([('model', '=', model_name)])
            if not model:
                raise ValidationError(
                    '无法根据模型名称【%s】找到模型记录，请检查模型名称是否正确' % (model_name or '空'))
            vals.update(model_id=model.id)
        return super(OAWorkflowRoute, self).create(vals)

    @api.constrains('model_id')
    def _check_model_id(self):
        if not self.is_custom and not self.model_id:
            raise ValidationError('非自定义路线需要指定关联模型！')

    def get_first_stage(self):
        return self.stage_ids.filtered(lambda r: r.is_start_stage)

    def get_record_valid_stages(self, record):
        # 获取当前记录的有效审批阶段
        need_filter_stages = self.stage_ids.filtered(lambda r: safe_eval(r.domain))
        valid_stages = self.stage_ids - need_filter_stages
        valid_stages |= need_filter_stages.filtered(
            lambda r: self.env[self.model_id.model].search_count(
                expression.AND([safe_eval(r.domain), [('id', '=', record.id)]])
            )
        )
        return valid_stages
        
    def get_next_stage(self, stage_id, record):
        if not stage_id:
            return self.get_first_stage()
        self._check_stage(stage_id)
        next_stage_ids = self.stage_ids.filtered(lambda r: r.sequence > stage_id.sequence)
        if next_stage_ids:
            for next_stage_id in next_stage_ids.sorted(lambda r: r.sequence):
                domain = safe_eval(next_stage_id.domain)
                if domain:
                    # 审批阶段包含过滤条件，先判断当前记录是否拥有相应的条件
                    if self.env[self.model_id.model].search_count(
                        expression.AND([domain, [('id', '=', record.id)]])):
                        return next_stage_id
                else:
                    return next_stage_id
        return False

    def get_pre_stage(self, stage_id):
        self._check_stage(stage_id)
        if stage_id.is_start_stage:
            #TODO: 如果返回False需要将工作流的state改为draft
            return False
        pre_stage_ids = self.stage_ids.filtered(lambda r: r.sequence < stage_id.sequence)
        if pre_stage_ids:
            return pre_stage_ids.sorted(lambda r: r.sequence)[-1]

    def _check_stage(self, stage_id):
        if not self.stage_ids & stage_id:
            raise UserError('审批阶段在工作流中不存在，审批阶段：%s' % stage_id and stage_id.name or 'null')

    def check_stage_ids(self):
        if not self.stage_ids:
            raise UserError('工作流审批路线不能为空！')
