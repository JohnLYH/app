{
    'name': '博益特-质检',
    'version': '1.0',
    'category': 'biote',
    'description': """
功能介绍
==============

* 放行单
* 不合格品处置单
    """,
    'author': '刘明臣',
    'website': 'http://openc2p.com',
    'depends': ['biote_base', 'biote_product', 'biote_stock'],
    'data': [       
        'data/stock_data.xml', 
        'views/biote_allow_item_views.xml',
        'views/biote_unqualified_handle_views.xml',
        'views/biote_unqualified_views.xml',
        'wizard/biote_allow_wiz_views.xml',
        'wizard/biote_unqualified_done_wiz_views.xml',
        'views/biote_quality.xml',
    ],    
    'installable': True,
    'auto_install': False,
}