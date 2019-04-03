from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools import image

from odoo.addons import decimal_precision as dp




class Teacher(models.Model):
    _name = "people.teacher"
    _inherit = ['mail.thread','mail.activity.mixin',]

    name = fields.Char(string='老师姓名')
    age = fields.Integer('年龄')
    active = fields.Boolean('任职', default=True)

    #货币表示
    # currency_id = fields.Many2one('res.currency', string='Currency')
    # salary=fields.Monetary( '收入',currency_field='currency_id',)

    salary = fields.Float('收入', digits=(8, 2),  track_visibility='onchange',)
    #小数精度控制另一种 需要安装decimal_precision模块 并在清单文件中声明 并在设置/数据库结构中进行配置
    # salary = fields.Float('收入', dp.get_precision('xinshui'), track_visibility='onchange',)


    #用于设置看板颜色等
    color = fields.Integer()

    tetosp = fields.Many2many('people.sports', string='对应运动')
    te2pe = fields.One2many('zz.peoples', 'petote', string='对应学生',)

    pay = fields.Float(string="税", digits=(3, 2), compute='_other')
    jiangjin = fields.Float('奖金', digits=(3, 2), compute='_jiang', store=True)

    # re = fields.Reference([('res.users', 'User'), ('res.partner', 'Partner')], '引用测试')
    #引用方式第二种 可在设置中添加引用模型
    re = fields.Reference(selection='referenceable_models', string='引用测试')

    #消息测试
    ar = fields.Selection(string="意见", selection=[('a', '同意'), ('r', '拒绝'), ], track_visibility='onchange', )

    @api.depends('salary')
    def _other(self):
        for re in self:
            re.pay = (re.salary) / 1000

    @api.depends('tetosp', 'te2pe')
    def _jiang(self):
        for re in self:
            re.jiangjin = (len(re.te2pe) + len(re.tetosp)) * 100

    # @api.onchange('salary')
    # def _warn(self):
    #     if self.salary < 10000:
    #         # self.salary+=500#不要在onchange方法对数据库进行更改
    #         return {'warning': {'title': "警报", 'message': "收入太少 活不下去了!", }, }

    @api.constrains('age')
    def _check_something(self):
        for record in self:
            if record.age > 80:
                raise ValidationError("年龄太大 该退休了: %s" % record.age)


    # 引用模型
    @api.model
    def referenceable_models(self):
        return [(link.object, link.name) for link in self.env['res.request.link'].search([])]

    #消息
    # 参考:message_type = fields.Selection([('email', 'Email'), ('comment', 'Comment'), ('notification', 'System notification')],'Type', required=True, default='email',
    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'ar' in init_values and (self.ar == 'a' or self.ar=='r'):
            self.message_post(body='哈mt_comment', message_type='comment', subtype='mail.mt_comment')
            # self.message_post(body='哈mt_note', message_type='comment', subtype='mail.mt_note')
            # self.message_post(body='哈notification', message_type='notification')
            # self.message_post(body='哈email', message_type='email')
            return 'zz.mailtest1'
        return super(Teacher, self)._track_subtype(init_values)


    #自定义名称显示方式   一般在many2one部件上有效果
    @api.multi
    # @api.depends('name', )
    def name_get(self):
        return [(r.id, (r.name + '同志')) for r in self]

     #自定义在关系字段小部件搜索时  不仅可以根据名字搜索  也可以根据年龄搜索
    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=2, name_get_uid=None):
        args = [] if args is None else args.copy()
        if not (name == '' and operator == 'ilike'):
            args += ['|', ('name', operator, name), ('age', operator, name)]
        return super(Teacher, self)._name_search(name='', args=args, operator='ilike', limit=limit,name_get_uid=name_get_uid)

    # --------------------按钮方法
    # @api.multi
    # def write2(self):
    #     self.write({'salary': (self.salary) + 1000})
    #     return True

    # 两种write方式都可以 write本身就可以同时更改多个数据

    @api.multi
    def write2(self):
        for rec in self:
            rec.write({'salary': (self.salary) + 100})
        return True


    #定时方法
    @api.model
    def write3(self):
        #每隔一会将薪水加100
        #api.model中的self仅代表模型本身 不含有任何记录信息 所以要先获得记录集
        s=self.search([])
        for rec in s:
            rec.write({'salary': (rec.salary) + 100})
        return True



    # 将年龄大于60的都隐藏
    @api.multi
    def bu1(self):
        dones = self.search([('age', '>', 60)])
        dones.write({'active': False})
        return True

    # 仅修改一个记录
    def bu2(self):
        self.active = False
        return True


    @api.multi
    def set_dead(self):
        return self.write({ 'active': False})


# ---------------------------------------------write和create方法重写


class Teacher2(models.Model):
    _inherit = 'people.teacher'

    img = fields.Char('老师头像')


#扩展write和create自动运行---运用这种方法模块加载时修改预填充数据
    @api.model
    def create(self, vals):
        # Code before create: can use the `vals` dict
        # 让新添加记录的人的年龄都自动加13
        vals['age'] += 13
        result = super(Teacher2, self).create(vals)
        # Code after create: can use the `result` created
        return result

    # @api.multi
    # def write(self, vals):
    #     # Code before write: can use `self`, with the old values
    #     if self.salary>1000000:
    #         vals={'salary':999999}
    #         super( ).write(vals)
    #     # Code after write: can use `self`, with the updated values
    #     return True

    # @api.multi
    # def write(self, vals):
    #     if self.id==4:
    #         vals={'active':False}
    #         super( ).write(vals)
    #     return True




# ------------------------附件相关
class Teacher3(models.Model):
    _inherit = ['people.teacher',]

    tou = fields.Binary('头像',)
    # tou2=fields.Char('头像2',compute='_tx' )

    # 附件上传
    # ia = fields.Many2many('ir.attachment', string='附件')
    ia = fields.Many2many('ir.attachment', compute='_getfjids', string='附件')


    def _getfjids(self):
        model = self.env['ir.attachment']  # 获取附件模型
        for obj in self:
            obj.ia = model.search([('res_model', '=', self._name), ('res_id', '=', obj.id)])  # 根据res_model和res_id查询附件取得附件list

    # @api.depends('tou')
    # def _tx(self):
    #     for i in self:
    #         i.tou2=(i.tou).decode('utf-8')


# 裁剪图片设置
# tou_small = fields.Binary('小小', compute="_get_image", store=True, attachment=True)
#
# @api.depends('tou')
# def _get_image(self):
#     for record in self:
#         if record.tou:
#             record.tou_small = image.crop_image(record.tou, type='top', ratio=(1, 1), size=(50, 50))
#         else:
#             record.tou_small = False







