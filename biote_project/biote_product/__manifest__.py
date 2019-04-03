{
    'name': '博益特-产品',
    'version': '1.0',
    'category': 'biote',
    'description': """
        产品列表,维护,分类;单位列表等
    """,
    'author': '张众',
    'website': 'http://openc2p.com',
    'depends': ['l10n_cn_small_business', 'biote_base', 'product', 'stock'],
    'data': [
        'data/ir_sequence_data.xml',
        'views/product_template_views.xml',
        'views/product_category_views.xml',
        'views/product_uom_views.xml',
        'views/product_uom_categ_views.xml',
        'views/biote_product_views.xml',
        'report/biote_product_category_templates.xml',
        'report/biote_product_reports.xml',
    ],
    'installable': True,
    'auto_install': False,
}
