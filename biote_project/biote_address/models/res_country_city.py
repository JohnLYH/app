import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class CountryCity(models.Model):
    _name = 'res.country.city'
    _description = "城市模型"

    state_id = fields.Many2one('res.country.state', string='省份')
    name = fields.Char(string='城市名称', required=True)
    ext = fields.Char(string='扩展id', default='0')


class CountryArea(models.Model):
    _name = 'res.country.area'
    _description = "区信息"

    city_id = fields.Many2one('res.country.city', string='城市')
    name = fields.Char(string='所在区', required=True)
    ext = fields.Char(string='扩展id', default='0')
