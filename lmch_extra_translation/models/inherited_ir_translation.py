# -*- coding: utf-8 -*-

import os
import logging
from os.path import join as opj

import odoo.tools as tools
from odoo import api, models
from odoo.modules import get_module_resource, get_module_path
from odoo.tools.misc import topological_sort

_logger = logging.getLogger(__name__)


def get_lmch_extra_file(m, lang_code):
    extra_module_dir = get_module_resource('lmch_extra_translation', 'extra_po', m)
    if extra_module_dir:
        file_path = opj(extra_module_dir, 'i18n', lang_code+'.po')
        if os.path.isfile(file_path):
            return file_path


class IrTranslation(models.Model):
    _inherit = "ir.translation"

    @api.model_cr_context
    def load_custom_module_terms(self, mods, langs):
        # 该操作耗时较长，将流程与系统原有流程分离。
        # res = super(IrTranslation, self).load_module_terms(modules, langs)

        mod_dict = {
            mod.name: mod.dependencies_id.mapped('name')
            for mod in mods
        }
        modules = topological_sort(mod_dict)

        res_lang = self.env['res.lang'].sudo()
        for lang in langs:
            res_lang.load_lang(lang)
        for module_name in modules:
            modpath = get_module_path(module_name)
            if not modpath:
                continue
            for lang in langs:
                context = dict(self._context)
                lang_code = tools.get_iso_codes(lang)
                lmch_extra_file = get_lmch_extra_file(module_name, lang_code)
                if lmch_extra_file:
                    _logger.info(u'模块 %s: loading lmch extra translation file (%s) for language %s', module_name,
                                 lang_code, lang)
                    tools.trans_load(self._cr, lmch_extra_file, lang, verbose=False, module_name=module_name,
                                     context=context)
        return True

    @api.model_cr_context
    def load_all_custom_module_terms(self, langs):
        mods = self.env['ir.module.module'].search([('state', '=', 'installed')])
        return self.load_custom_module_terms(mods, langs)


