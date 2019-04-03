{
    'name': '博益特-采购管理',
    'version': '1.0',
    'category': 'biote',
    'description': """
    """,
    'author': '张众,刘明臣',
    'website': 'http://openc2p.com',
    'depends': [
        'oa_workflow',
        'biote_base',
        'biote_product',
        'biote_hr',
        'biote_partner',
        'biote_quality'
    ],
    'data': [
        'data/ir_sequence_data.xml',
        'data/stock_data.xml',
        'views/biote_assets_purchase_views.xml',
        'views/biote_purchase_plan_views.xml',
        'views/biote_purchase_recevie_views.xml',
        # 原材料放行单
        'views/biote_allow_views.xml',
        'views/biote_purchase_views.xml',
        'report/biote_purchase_plan_templates.xml',
        'report/biote_purchase_reports.xml',
        'views/biote_contract_views.xml',
        'views/inherited_biote_stock_picking_views.xml'
    ],
    'installable': True,
    'auto_install': False,
}
