# -*- coding: utf-8 -*-
{
    'name' : 'tredeco modification ',
    'version' : '1.0',
    'category': '',
    'description': """
   tredeco_modification used to show or hid  smart buttons cost analysis from product view and structure and cost from bill of materials and cost analysis smart buttons from manufacturing order 
   and create security groups in user settings to control on display buttons or hid it 
   you will find this groups under Category called >>Show Cost analysis and cost structure Smart Buttons

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