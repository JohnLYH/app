{
    'name': '博益特-合作伙伴',
    'version': '1.0',
    'category': 'biote',
    'description': """
功能介绍
==============
* 博益特客户，供应商信息录入
* 合伙伙伴资质证书信息录入
* 地址信息完善
* 财务信息完善
* 合作伙伴批量excel导入
    """,
    'author': '吕红园',
    'website': 'http://openc2p.com',
    'depends': ['l10n_cn_small_business', 'biote_base', 'biote_hr', 'biote_bank', 'biote_address'],
    'data': [
        'data/ir_default.xml',
        'views/res_partner_views.xml',
        'views/qualification_document_views.xml',
        'views/biote_partner_views.xml',
        'views/biote_partner_finance.xml',
        'data/customer_category_data.xml',
        'wizard/partner_data_transient_views.xml',
        'wizard/partner_transient_views.xml',
        'views/assets.xml',
        'data/ir_sequence.xml',
        'data/biote_payment_data.xml',
    ],    
    'installable': True,
    'auto_install': False,
}
