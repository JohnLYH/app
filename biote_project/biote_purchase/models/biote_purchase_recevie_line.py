import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero

_logger = logging.getLogger(__name__)


class BiotePurchaseRecevieLine(models.Model):
    _name = 'biote.purchase.recevie.line'
    _description = '收货四联单明细'

    name = fields.Char(ralated='recevie_id.name', string='收货单据编号')
    # TODO: 界面中添加过滤条件，只选择原辅料与包材类别
    product_id = fields.Many2one(comodel_name='product.product', string='物料名称')
    lot_name = fields.Char(string='批号')
    ordered_qty = fields.Float(string='订购数量')
    recevie_qty = fields.Float(string='收货数量')
    # 一个收货行可能对应多个放行单，例如收货行A（收货数量12）生成放行单B（此时A的生成放行单选项被锁定），B执行了放行5
    # 操作，B放行单的未放行数量为7，A的状态为部分处理，剩余未处理数量为7
    remaining_qty = fields.Float(
        string='剩余数量',
        help='收货数量-sum(放行)-sum(未放行)',
        compute='_compute_remaining_qty',
        store=True
    )
    receive_date = fields.Date(string='收货日期')
    recevie_id = fields.Many2one(comodel_name='biote.purchase.recevie', string='收货四联单')
    raw_allow_ids = fields.One2many(
        comodel_name='biote.allow', inverse_name='recevie_line_id', string='放行单号')
    # 一个采购收货明细选择放行后生成一个放行单，此时该收货行明细不能再产生放行单，必须等到产生的放行单处理完成才可以继续生成下一个放行单。
    # 当所有完成状态（放行或者不放行）的放行单放行或者不放行数量总和为收货数量时，该收货行的放行状态为已完成。
    # 注意：收货行的完成状态与放行单的入库或者不放行的不合格处置单的状态不进行关联。只要不放行或者放行总量达到收货数量即视为放行完成。
    allow_state = fields.Selection(
        string='放行单状态',
        selection=[
            ('draft', '未进行'),
            ('process', '放行中'),
            ('partially', '部分处理'),
            ('done', '完成')
        ],
        help='放行单是按照顺序依次创建的，只有当放行单填入数量并且审核完成后才能为剩余数量继续创建下一个放行单',
        compute='_compute_remaining_qty',
        store=True
    )
    allow_amount_qty = fields.Float(
        string='放行总量',
        compute='_compute_remaining_qty',
        help='所有放行单的放行数量之和',
        store=True
    )
    refused_amount_qty = fields.Float(
        string='未放行总量',
        compute='_compute_remaining_qty',
        store=True
    )

    def _get_allow_line(self):
        # 获取可以创建放行单的收货明细
        return self.filtered(
            lambda r: r.allow_state in ('draft', 'partially') and r.recevie_qty > 0)
    
    @api.depends('recevie_qty', 'raw_allow_ids', 'raw_allow_ids.state')
    def _compute_remaining_qty(self):
        # float_is_zero方法使用产品单位精度
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for line in self:
            if not line.raw_allow_ids:
                line.allow_state = 'draft'
                line.remaining_qty = line.recevie_qty
            else:
                # 获取放行状态不为空的放行单
                done_allow_ids = line.raw_allow_ids.filtered(lambda r: r.state != 'draft')
                line.allow_amount_qty = sum(done_allow_ids.mapped('allow_qty'))
                line.refused_amount_qty = sum(done_allow_ids.mapped('refused_qty'))
                line.remaining_qty = line.recevie_qty - line.allow_amount_qty - line.refused_amount_qty
                if line.raw_allow_ids.filtered(lambda r: r.state == 'draft'):
                    line.allow_state = 'process'
                else:
                    if float_is_zero(line.remaining_qty, precision):
                        line.allow_state = 'done'
                    else:
                        line.allow_state = 'partially'

    @api.multi
    def action_create_raw_allow(self):
        for line in self:
            # 取消放行单时需要改变收货明细的放行状态allow_state
            line.allow_state = 'process'
            self.env['biote.allow'].create({
                'product_id': line.product_id.id,
                'recevie_line_id': line.id,
                'allow_type': 'raw'
            })
        return True