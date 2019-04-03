{
    'name': '工作流测试',
    'version': '1.0',
    'category': '',
    'description': """
功能介绍
==============

* 完成测试
    * 部门成员审批
    * 部门主管审批
    * 指定人员审批
    * 工作流开启子审批
    * 根据记录的不同状态选择不同的审批阶段
    * 根据记录的不同状态选择不同的审批路线
    """,
    'author': 'lmch',
    'website': 'http://openc2p.com',
    'depends': ['oa_workflow'],
    'data': [
        'data/test_data.xml',
        'views/oa_simple_test_views.xml',
        'security/ir.model.access.csv'
    ],    
    'installable': True,
    'auto_install': False,
}

# 阶段的名称生成方式 如果有部门且是全员则 部门+审批，如果是主管 部门+主管+审批，如果只有个人则取 人名+审批
# 点击 -> 选择审批人或者审批部门 -> 根据当前阶段创建分支工作流 -> 