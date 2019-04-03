# -*- coding: utf-8 -*-

{
    'name': 'Otoo自定义翻译',
    'version': '1.0',
    'category': '',
    'description': """
模块介绍
=========

将自定义的翻译文件从系统模块中分离出来。

使用
---------
* 设置->翻译->加载自定义翻译。
* 附加的po文件开头需要添加 msgid ""与msgstr ""(占用两行，跳过机制)
    """,
    'author': 'lmch',
    'website': '',
    'depends': ['base'],
    'data': [
        'wizard/base_language_install_views.xml'
    ],
    'installable': True,
    'auto_install': False,
}
