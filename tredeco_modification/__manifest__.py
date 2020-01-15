# -*- coding: utf-8 -*-
{
    'name' : 'tredeco modification ',
    'version' : '1.0',
    'category': '',
    'description': """
   tredeco modification to remove smart buttons cost analysis from product view and structure and cost from bill of matrials

    """,
    'depends' : ['base','mrp_account','mrp'],
    'data': [
        'security/security_groups_view.xml',
        'views/product_template_custom.xml',
        'views/manufacturing_view_custom.xml',

    ],
    'installable': True,
    'application': True,
}