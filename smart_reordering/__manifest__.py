# -*- coding: utf-8 -*-
{
    'name': "Smart Reordering",

    'summary': """
        """,

    'description': """
        
    """,

    'author': "Ergo Ventures Ltd.",
    'website': "http://www.ergo-ventures.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock','purchase_stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/product_template_view.xml',
        'views/purchase.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}