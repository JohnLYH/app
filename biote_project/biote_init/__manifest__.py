{
    'name': '博益特-项目初始化',
    'version': '1.0',
    'category': 'biote',
    'description': """
功能介绍
==============

* 实现项目的一键创建功能
* 安装博益特项目的所有模块，按照模块依赖关系从叶子节点开始安装
* 导入初始化数据
* 进行基础配置
    """,
    'author': '刘明臣',
    'website': 'http://openc2p.com',
    'depends': [
        'product',
        'stock',
        'hr',
        'l10n_cn',
        'l10n_cn_small_business',
        'form_no_edit',
        'oa_workflow',
        'biote_bank',
        'biote_address',
        'biote_product',
        'biote_auth',
        'biote_contract',
        'biote_partner',
        'biote_quality',
        'biote_purchase'
    ],
    'data': [],    
    'installable': True,
    'auto_install': False,
}