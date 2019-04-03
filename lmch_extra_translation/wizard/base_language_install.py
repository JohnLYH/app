# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class BaseLanguageInstall(models.TransientModel):

    _inherit = "base.language.install"

    is_load_all = fields.Boolean(u'加载所有', default=False, help=u'选择后将加载所有已安装模块的翻译文件')
    load_module = fields.Many2one('ir.module.module', string=u'加载模块', domain=[('state', '=', 'installed')])

    @api.multi
    def custom_install_lang(self):
        self.ensure_one()
        translation_obj = self.env['ir.translation'].with_context(overwrite=self.overwrite)
        if self.is_load_all:
            translation_obj.load_all_custom_module_terms([self.lang])
        else:
            translation_obj.load_custom_module_terms(self.load_module, [self.lang])

        self.state = 'done'
        return {
            'name': _('Language Pack'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'base.language.install',
            'domain': [],
            'context': dict(self._context, active_ids=self.ids),
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
        }
