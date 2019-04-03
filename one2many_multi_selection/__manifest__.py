
{
    'name': "one2many_multi_selection",
    'depends': ['base', 'sale', 'purchase', 'mrp','zz'],
    'data': [
        'views/views.xml',
        'views/templates.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}