{
    'name': '博益特-库存管理',
    'version': '1.0',
    'category': 'biote',
    'description': """
功能介绍
==============

* 博益特作业类型
* 博益特库存调拨单
* 博益特库存移动单
    """,
    'author': '刘明臣',
    'website': 'http://openc2p.com',
    'depends': ['biote_base', 'stock'],
    'data': [
        'views/biote_stock_move_views.xml',
        'views/biote_stock_picking_type_views.xml',
        'views/biote_stock_picking_views.xml',
        'views/inherited_stock_location_views.xml',
        'views/inherited_stock_warehouse_views.xml',
        'views/biote_stock.xml',
        'data/biote_stock_data.xml'
    ],    
    'installable': True,
    'auto_install': False,
}