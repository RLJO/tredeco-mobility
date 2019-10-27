# -*- coding: utf-8 -*-
{
    'name': "Tredco access writes",
    'summary': """
        """,
    'description': """
        
    """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['sale', 'stock', 'purchase','repair'],

    # always loaded
    'data': [

        'security/repair.xml',
        'views/purchase.xml',
        'views/sale_order.xml',
        'views/stock_picking.xml',
        'views/repair.xml',
    ],
}