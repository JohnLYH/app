{
    'name': '原生视图扩展',
    'version': '1.0',
    'category': '',
    'description': """
功能介绍
==============

* 禁止o2m视图列表点击，下列方法二选一即可
    * 视图中o2m字段的tree定义添加属性context={'disable_open': 1}
    * 视图中o2m字段中添加属性context={'disable_open': 1}
* decoration-danger与decoration-warning修饰的列表，行的背景会变色
* 添加列表选择对话框
    """,
    'author': 'lmch',
    'website': 'http://openc2p.com',
    'depends': ['web'],
    'data': [
        'views/assets.xml'
    ],    
    'installable': True,
    'auto_install': False,
}