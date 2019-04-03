{
    'name': '博益特-授权书',
    'version': '1.0',
    'category': 'biote',
    'description': """
功能介绍
==============
* 申请授权
* 打印授权书
    """,
    'author': '吕红园',
    'website': 'http://openc2p.com',
    'depends': ['biote_hr', 'biote_address', 'biote_partner', 'biote_product'],
    'data': [
        'views/biote_auth_main_views.xml',
        'views/biote_auth_views.xml',
        'data/ir_default.xml',
        'data/ir_sequence.xml',
        'report/auth_report.xml',
        'report/auth_report_templates.xml',
        'report/custom_external_layout_templates.xml',
        'views/assets.xml',
    ],    
    'installable': True,
    'auto_install': False,
}