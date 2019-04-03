{
    'name': '工作流',
    'version': '1.0',
    'category': '',
    'description': """
功能介绍
==============

* 支持在界面为需要进行审批的模型自定义审批路线
* 支持审批阶段根据被审批单据的字段值进行过滤
* 支持审批路线根据被审批单据的字段值进行筛选
* 使用系统模型或者自定义模型与oa.workflow.mixin类进行组合，组合后的模型可以通过设置->工作流配置->工作流路线对模型配置不同的路线
* 通过xml可以为绑定工作流的模型配置预设路线，参考test_oa_workflow
* 工作流的表单设计参考test_oa_workflow
    """,
    'author': 'lmch',
    'website': 'http://openc2p.com',
    'depends': ['hr', 'basic_view_ext'],
    'data': [
        'wizard/oa_workflow_opinion_wiz_views.xml',
        'wizard/oa_subflow_wiz_views.xml',
        'wizard/oa_subflow_detail_wiz_views.xml',
        'security/ir.model.access.csv',
        'views/oa_workflow.xml',
        'views/oa_workflow_route_views.xml',
        'views/oa_workflow_result.xml',
        'views/oa_workflow_stage_views.xml',
    ],    
    'installable': True,
    'auto_install': False,
}