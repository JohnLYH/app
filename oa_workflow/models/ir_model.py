import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class IrModel(models.Model):
    _inherit = 'ir.model'

    is_workflow = fields.Boolean(string="工作流审批", default=False, help="模型是否支持工作流审批")
    
    def _reflect_model_params(self, model):
        vals = super(IrModel, self)._reflect_model_params(model)
        vals['is_workflow'] = issubclass(type(model), self.pool['oa.workflow.mixin']) and \
        model._name != 'oa.workflow.mixin'
        return vals