{
    'name': '博益特-财务管理',
    'version': '1.0',
    'category': 'biote',
    'description': """
功能介绍
==============

* 财务管理
    """,
    'author': '赵英涵',
    'website': 'http://openc2p.com',
    'depends': ['biote_hr', 'biote_bank', 'decimal_precision'],
    'data': [
        'data/ir_sequence_data.xml',
        'data/biote_account_data.xml',
        'views/biote_expense_views.xml',
        'views/biote_account_views.xml',
        'views/biote_payment_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
