{
    'name': "博益特-合同",
    'version': '1.0',
    'category': 'biote',
    'description': """
功能
====
* 博益特合同审批
* 合同审批后打印
""",
    'author': "吕红园",
    'website': "http://openc2p.com",
    'depends': ['web', 'biote_base', 'oa_workflow'],
    'data': [
        'data/test_data.xml',
        'data/ir_sequence.xml',
        'views/assets.xml',
        'views/biote_contract_main_views.xml',
        'views/biote_contract_views.xml',
        'views/state.xml',
        'views/route.xml',
        'views/menu.xml',
        'security/ir.model.access.csv',
        'report/inherit_web_layout_templates.xml',
        'report/biote_contract_report.xml',
        'report/biote_contract_report_templates.xml',

    ],
    'installable': True,
    'auto_install': False,
}

