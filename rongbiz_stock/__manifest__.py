{
    'name': '容商库存管理模块',
    'version': '1.0',
    'category': '',
    'description': """
功能介绍
==============

* 采购入库单
* 出库单
* 供应商管理
* 领料人管理
* 批次号绑定价格
    """,
    'author': 'lmch',
    'website': 'http://openc2p.com',
    'depends': [
        'stock',
        'purchase',
        'sale_management',
        'sale_stock',
        'l10n_cn_small_business',
        'lmch_extra_translation',
        'web_export_view',
        'web_group_expand'
    ],
    'data': [
        'data/product_template_data.xml',
        'data/purchase_order_data.xml',
        'data/sale_order_data.xml',
        'security/security.xml',
        'views/product_category.xml',
        'views/product_template.xml',
        'views/res_partner_views.xml',
        'views/purchase_order_views.xml',
        'views/sale_order_views.xml',
        'views/purchase_order_line_views.xml',
        'views/sale_order_line_views.xml',
        'views/stock_production_lot_views.xml',
        'views/rongbiz_stock.xml',
        'views/hide_menu_views.xml',
        'views/assets.xml',
        'views/inherited_views.xml',
        'security/ir.model.access.csv',
        'wizard/product_data_transient_views.xml',
    ],
    'qweb': [
        "static/src/xml/hide_filter.xml",
    ],
    'installable': True,
    'auto_install': False,
}