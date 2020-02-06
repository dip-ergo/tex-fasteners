# -*- coding: utf-8 -*-
{
    'name': "Syncoria Discrepancy Report",

    'summary': """
        * Show discrepancy report for SO, DO and MO""",

    'description': """
        * Show discrepancy report for SO, DO and MO
    """,

    'author': "Syncoria",
    'website': "http://www.syncoria.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mrp','stock','sale','purchase', 'sale_stock', 'mto_chain'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/discrepancy_template.xml',
        'views/so_line_view.xml',
        'views/discrepancy_view.xml',
    ],
    'qweb': [
        'static/src/xml/discrepancy_report_backend.xml',
        # 'static/src/xml/discrepancy_report_line.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}