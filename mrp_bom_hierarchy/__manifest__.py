# -*- coding: utf-8 -*-

{
    'name': 'BoM层级视图',
    'version': '1.0',
    'category': '',
    'description': """
功能
====

* 为BoM清单添加层级视图
    """,
    'author': 'lmch',
    'website': 'http://www.rongbiz.com',
    'depends': ['mrp'],
    'data': [
        'views/assets.xml',
        'views/mrp_bom_hierarchy_tml.xml',
        'views/mrp_bom_hierarchy_views.xml'
    ],
    'qweb': [
        'static/src/xml/mrp_bom_hierarchy_fold.xml'
    ],
    'installable': True,
    'auto_install': True,
}
