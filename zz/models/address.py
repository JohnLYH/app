# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class Province(models.Model):
    _name = 'zz.province'
    #如果模型中没有name字段  需要rec_name指定显示名称
    # _rec_name = 'pname'

    name= fields.Char('省')


class City(models.Model):
    _name = 'zz.city'

    name = fields.Char('市')
    c2p = fields.Many2one('zz.province', string="省")


class Town(models.Model):
    _name = 'zz.town'

    name = fields.Char('乡')
    t2c = fields.Many2one('zz.city', string="市")



