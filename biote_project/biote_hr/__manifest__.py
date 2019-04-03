{
    'name': '博益特-员工',
    'version': '1.0',
    'category': 'biote',
    'description': """
功能介绍
==============

* 博益特-员工
    """,
    'author': '赵英涵',
    'website': 'http://openc2p.com',
    'depends': ['hr'],
    'data': [
        'views/assets.xml',
        'data/ir_sequence_data.xml',
        'views/hr_department_views.xml',
        'views/hr_education_views.xml',
        'views/hr_training_views.xml',
        'views/hr_work_exp_views.xml',
        'views/hr_family_views.xml',
        'views/hr_employee_views.xml',
        'views/biote_hr_views.xml',
        'report/hr_employee_templates.xml',
        'report/hr_employee_report.xml',
        'wizard/import_hr_data_wizard_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
