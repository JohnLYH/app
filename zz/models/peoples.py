from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError,except_orm


class Sports(models.Model):
    _name = 'people.sports'

    name = fields.Char(string='运动项目')
    color = fields.Integer()


class Peoples(models.Model):
    _name = 'zz.peoples'
    _inherit ='mail.thread'

    name = fields.Char(string='姓名')
    id = fields.Integer(string='ID')

    img = fields.Char(string='头像')
    age = fields.Integer(string='年龄')
    des = fields.Text(string='描述')
    color = fields.Integer()

    zongfen = fields.Integer(string='总分', compute='_zf')
    priority = fields.Selection([('0', 'Very Low'), ('1', 'Low'), ('2', 'Normal'), ('3', 'High'), ('4', 'Very High')],'优先级', default='1')

    petosp = fields.Many2many(comodel_name='people.sports', string='对应运动')
    petote = fields.Many2one('people.teacher', string='对应老师')

    @api.depends('yuwen', 'shuxue', 'yingyu')
    def _zf(self):
        for r in self:
            r.zongfen = r.yuwen + r.shuxue + r.yingyu


# 唯一性约束
    # _sql_constraints = [('only_id', 'UNIQUE(name)','姓名要唯一')]

    # @api.constrains('name')
    # def nameonly(self):
    #     names=self.search([('name','=',self.name)])
    #     if len(names)>1:
    #         raise ValidationError('name要唯一')
    #         # raise except_orm('name要唯一')



# 同一文件继承放在后
class Subject(models.Model):
    _inherit = 'zz.peoples'

    name = fields.Char(string='姓名')
    yuwen = fields.Integer(string='语文', )
    shuxue = fields.Integer(string='数学', )
    yingyu = fields.Integer(string='英语', )


    #related使二者相关联 family_id取值 则city也取值
    family_id = fields.Many2one('res.partner', string='家人')
    city = fields.Char('家人.城市', related='family_id.city', readonly=True)




class Peopletest(models.Model):
    _inherit = 'zz.peoples'

    ia = fields.Many2many('ir.attachment', string='附件')
    active=fields.Boolean('有效',default=True)

    # 测试隐藏设置 点击on_change字段出现gender 模块内配置
    on_change = fields.Boolean('显示隐藏项', )
    gender = fields.Selection(selection=[('1', 'Male'), ('0', 'Female')],string='性别')

    # 测试隐藏设置 配置到系统设置
    health=fields.Selection(selection=[('1', 'GOOD'), ('0', 'BAD')],string='健康状况',groups='zz.hidden',default='1')

    # 测试审批流
    state = fields.Selection([('small', 'Small'), ('big', 'Big'),('middle', 'Middle'), ], '状态', default='small', )



    @api.multi
    def set_small(self):
        return self.write({ 'state': 'small'})

    @api.multi
    def set_big(self):
        return self.write({ 'state': 'big'})

    @api.multi
    def set_middle(self):
        return self.write({ 'state': 'middle'})


# ---地址
class Address(models.Model):
    _inherit = 'zz.peoples'

    p = fields.Many2one('zz.province', string='省')
    c = fields.Many2one('zz.city', string='市')
    t = fields.Many2one('zz.town', string='乡')
    aname = fields.Char('地址', compute='_compute_aname', )

    # 列表视图中全名显示方式
    @api.depends('p', 'c', 't')
    def _compute_aname(self):
        for a in self:
            if a.p.name:
                #or '' 防止出现值显示为False
                a.aname = '%s   %s   %s' % (a.p.name or '', a.c.name or '', a.t.name or '')
            else:
                a.aname = '暂未填写'

    # 防止填完后 重新修改前面的值 而后面的值不变的问题出现
    @api.onchange('p')
    def _onchange_c(self):
        self.c = None

    @api.onchange('c')
    def _onchange_t(self):
        self.t = None
