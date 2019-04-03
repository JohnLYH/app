import logging

from odoo import models, fields, api, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class BioteBaseModel(models.AbstractModel):
    _name = 'biote.base.model'
    
    biote_audit_state = fields.Selection(
        string='审核状态', 
        selection=[('open', '审核中'), ('done', '已审核'), ('re-open', '重新审核')]
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='公司名称',
        required=True,
        default=lambda self: self.env.user.company_id
    )

    def _get_workflow_state(self):
        # 判断模型是否使用了工作流审批，如果是则返回当前的审批状态，如果否则返回False
        # 工作流创建时的默认状态为draft
        return getattr(self, 'workflow_state', False)
    
    def action_biote_audit_reopen(self):
        # 只有管理员或者记录的发起人才能对表单进行反审核操作
        is_admin = self.env.user.has_group('biote_base.biote_base_group_admin') or \
        self.env.uid == SUPERUSER_ID
        for rec in self:
            if not (is_admin or self.env.uid == rec.create_uid):
                raise UserError('没有反审核操作权限！')
            workflow_state = rec._get_workflow_state()
            if  workflow_state and workflow_state != 'draft':
                raise UserError('不能对审批中以及审批完成的单据发起反审核操作！')
            rec.update({'biote_audit_state': 're-open'})

    def action_biote_audit_done(self):
        for rec in self:
            workflow_state = rec._get_workflow_state()
            if workflow_state and workflow_state != 'done':
                raise UserError('不能对未审批结束的单据进行审核操作')
            rec.update({'biote_audit_state': 'done'})

    def workflow_done_callback(self):
        # 工作流完成时的回调
        if self._get_workflow_state():
            # TODO: 是否需要使用sudo来进行操作？最后一个审批人是否具有审核权限？
            self.action_biote_audit_done()
