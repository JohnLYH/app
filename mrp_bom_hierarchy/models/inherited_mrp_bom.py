# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.model
    def get_bom_hierarchy_html(self, given_context=None):
        active_id = given_context.get('active_id')
        bom = self.search([('id', '=', active_id)])
        html = self.env.ref('mrp_bom_hierarchy.mrp_bom_hierarchy').render(values={'docs': bom})
        res = {
            'html': html
        }
        return res

    def get_bom_children(self, level=0):
        result = []

        def _get_rec(object, level, qty=1.0, uom=False):
            for l in object:
                res = {}
                res['pname'] = l.product_id.name_get()[0][1]
                res['pcode'] = l.product_id.default_code
                qty_per_bom = l.bom_id.product_qty
                if uom:
                    if uom != l.bom_id.product_uom_id:
                        qty = uom._compute_quantity(qty, l.bom_id.product_uom_id)
                    res['pqty'] = (l.product_qty *qty)/ qty_per_bom
                else:
                    #for the first case, the ponderation is right
                    res['pqty'] = (l.product_qty *qty)
                res['puom'] = l.product_uom_id
                res['uname'] = l.product_uom_id.name
                res['level'] = level
                res['code'] = l.bom_id.code
                res['res_id'] = l.id
                res['res_model'] = 'mrp.bom.line'
                result.append(res)
                if l.child_line_ids:
                    # 点击折叠后会将该bom的直接子集折叠
                    res['child_line_ids'] = l.child_line_ids.mapped('id')
                    res['is_leaf'] = False
                    # if level < 6:
                    level += 1
                    _get_rec(l.child_line_ids, level, qty=res['pqty'], uom=res['puom'])
                    # if level > 0 and level < 6:
                    level -= 1
                else:
                    res['is_leaf'] = True
            return result

        children = _get_rec(self.bom_line_ids, level)

        return children
