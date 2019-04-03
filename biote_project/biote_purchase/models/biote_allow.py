import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero

_logger = logging.getLogger(__name__)


class BioteAllow(models.Model):
    _inherit = 'biote.allow'

    recevie_line_id = fields.Many2one(comodel_name='biote.purchase.recevie.line', string='收货单明细')
    allow_type = fields.Selection(selection_add=[('raw', '原材料放行单')])
    incoming_state = fields.Selection(
        string='入库状态',
        selection=[
            ('draft', '未进行'),
            ('process', '入库中'),
            ('partially', '部分入库'),
            ('done', '完成')
        ],
        compute='_compute_incoming_qty',
        store=True
    )
    move_ids = fields.One2many(
        comodel_name='biote.stock.move',
        inverse_name='allow_id',
        string='库存移动明细',
        help='放行单关联的原材料采购库存移动明细'
    )
    incoming_amount_qty = fields.Float(
        string='入库总数量', compute='_compute_incoming_qty', store=True
    )
    incoming_remaining_qty = fields.Float(
        string='未入库数量', compute='_compute_incoming_qty', store=True
    )

    def _get_incoming_allow(self):
        # 获取可以生成入库单的放行单
        return self.filtered(
            lambda r: r.state == 'approve' and r.incoming_state in ('draft', 'partially')
        )

    def _get_recevie_id(self):
        # 获取放行单对应的收货四联单ID
        recevie_ids = self.mapped('recevie_line_id').mapped('recevie_id')
        recevie_ids = list(set(recevie_ids))
        if len(recevie_ids) != 1:
            raise UserError('收货四联单数量错误！')
        return recevie_ids[0]

    @api.depends('state', 'move_ids', 'move_ids.state')
    def _compute_incoming_qty(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for approve_allow in self.filtered(lambda r: r.state == 'approve'):
            approve_allow.incoming_amount_qty = sum(approve_allow.move_ids.filtered(
                lambda r: r.state == 'done').mapped('move_qty'))
            approve_allow.incoming_remaining_qty = approve_allow.allow_qty - approve_allow.incoming_amount_qty
            if not approve_allow.move_ids:
                approve_allow.incoming_state = 'draft'
                continue
            if float_is_zero(approve_allow.incoming_remaining_qty, precision):
                approve_allow.incoming_state = 'done'
            else:
                if approve_allow.move_ids.filtered(lambda r: r.state == 'draft'):
                    approve_allow.incoming_state = 'process'
                else:
                    approve_allow.incoming_state = 'partially'

    @api.multi
    def action_create_incoming(self):
        # 创建采购入库单
        incoming_allows = self._get_incoming_allow()
        if incoming_allows:
            raw_incoming_type = self.env['biote.stock.picking.type']._get_specific_type('raw_incoming')
            recevie_id = incoming_allows._get_recevie_id()
            incoming_vals = {
                'move_ids': incoming_allows.mapped(
                    lambda r: (0, 0, {
                        'product_id': r.product_id.id,
                        'move_qty': r.incoming_remaining_qty,
                        'allow_id': r.id,
                        'location_id': raw_incoming_type.location_id.id,
                        'dest_warehouse_id': raw_incoming_type.dest_warehouse_id.id
                    })
                ),
                'picking_type_id': raw_incoming_type.id,
                'recevie_id': recevie_id.id
            }
            self.env['biote.stock.picking'].create(incoming_vals)

    def _get_allow_wiz(self):
        action = super(BioteAllow, self)._get_allow_wiz()
        if self.allow_type == 'raw':
            max_qty = self.recevie_line_id.remaining_qty
            action['context'].update(default_max_qty=max_qty)
        return action