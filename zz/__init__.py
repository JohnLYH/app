from . import models
from . import controllers

# 导入自定义报表rep
from . import report





from odoo import api, SUPERUSER_ID

def post_init_hook(cr,registry):
    #获取超级用户环境
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['people.teacher'].search([('age', '>',60)]).unlink()