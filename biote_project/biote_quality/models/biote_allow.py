import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero

_logger = logging.getLogger(__name__)


class BioteAllow(models.Model):
    _name = 'biote.allow'
    _description = '放行单'

    name = fields.Char(string='单据编号')
    product_id = fields.Many2one(comodel_name='product.product', string='产品名称')
    allow_type = fields.Selection(string='放行单类型', selection=[])
    allow_qty = fields.Float(string='放行数量')
    refused_qty = fields.Float(string='不放行数量')
    quality_consume_qty = fields.Float(string='质检消耗数量')
    unqualified_ids = fields.One2many(
        comodel_name='biote.unqualified', inverse_name='refused_allow_id', string='不合格处置单')
    # 根据allow_type在放行单的视图定义中指定domain
    allow_item_ids = fields.Many2many(comodel_name='biote.allow.item', string='放行审核内容')
    state = fields.Selection(
        string='是否放行',
        selection=[('draft', '草稿'), ('approve', '放行'), ('refused', '不放行')],
        default='draft'
    )
    unqualified_amount_qty = fields.Float(
        string='不合格处置总量',
        compute='_compute_unqualified_qty',
        store=True
    )
    unqualified_remaining_qty = fields.Float(
        string='未处置数量', 
        help='放行数量使用入库单进行处置，未放行数量使用不合格处置单进行处置，处置完成该值变为0',
        compute='_compute_unqualified_qty',
        store=True
    )
    unqualified_state = fields.Selection(
        string='不合格处置单状态',
        selection=[
            ('draft', '未进行'),
            ('process', '处置中'),
            ('partially', '部分处置'),
            ('done', '完成')
        ],
        help='处置单是按照顺序依次创建的，只有当处置单填入数量并且审核完成后才能为剩余数量继续创建下一个处置单',
        compute='_compute_unqualified_qty',
        store=True
    )

    @api.depends('state', 'unqualified_ids', 'unqualified_ids.state')
    def _compute_unqualified_qty(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        # 计算不放行单未进行不合格处置的数量
        for refused_allow in self.filtered(lambda r: r.state == 'refused'):
            # if refused_allow.state == 'draft':
            #     # 新建放行单时需要给不合格处置状态设置一个值
            #     refused_allow.unqualified_state = 'draft'
            #     continue
            # 剩余数量依赖于不合格处置单的状态，只有完成状态的不合格处置单才会影响放行单的未处置数量，需要在依赖字段中声明
            refused_allow.unqualified_amount_qty = sum(
                refused_allow.unqualified_ids.filtered(lambda r: r.state == 'done').mapped('handle_qty')
            )
            refused_allow.unqualified_remaining_qty = refused_allow.refused_qty - refused_allow.unqualified_amount_qty
            if not refused_allow.unqualified_ids:
                refused_allow.unqualified_state = 'draft'
                continue
            if float_is_zero(refused_allow.unqualified_remaining_qty, precision):
                # 剩余数量为0，未放行单已完成
                refused_allow.unqualified_state = 'done'
            else:
                if refused_allow.unqualified_ids.filtered(lambda r: r.state == 'process'):
                    refused_allow.unqualified_state = 'process'
                else:
                    refused_allow.unqualified_state = 'partially'
                    
    def _get_allow_wiz(self):
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'name': '放行单',
            'res_model': 'biote.allow.wiz',
            'target': 'new',
            'context': {
                'default_allow_id': self.id
            }
        }

    def action_approve(self):
        self.ensure_one()
        # 注意不能再改按钮方法中执行状态改变
        action = self._get_allow_wiz()
        action['context'].update({
            'default_state': 'approve'
        })
        return action

    def action_refused(self):
        self.ensure_one()
        action = self._get_allow_wiz()
        action['context'].update({
            'default_state': 'refused'
        })
        return action

    def _get_unqualified_allow(self):
        # 获取可以生成不合格处置单的放行单
        return self.filtered(
            lambda r: r.state == 'refused' and r.unqualified_state in ('draft', 'partially'))
        
    @api.multi
    def action_create_unqualified(self):
        # 通过未放行单创建不合格处置单
        for refused in self._get_unqualified_allow():
            self.env['biote.unqualified'].create({
                'refused_allow_id': refused.id,
                'product_id': refused.product_id.id,
                'handle_qty': refused.refused_qty
            })  

    @api.multi
    def action_done(self, state, allow_qty, refused_qty):
        self.ensure_one()
        self.write({
            'state': state,
            'allow_qty': allow_qty,
            'refused_qty': refused_qty
        })
