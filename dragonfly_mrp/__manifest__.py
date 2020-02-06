# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Dragon Fly MRP Enhancement',
    'summary': 'Dragon Fly MRP Enhancement',
    'sequence': 100,
    'license': 'OEEL-1',
    'website': 'https://www.odoo.com/page/manufacturing',
    'version': '1.1',
    'author': 'Odoo Inc',
    'description': """
MRP Enhancement
===============

* [1938284]
    -  This will add a button ('Documents') on the work order process screen that will create a new tab in the browser with the attachment screen of the product
       that is selected on the related manufacturing order.
* [1935396]
    - Quality checks with (tokenized) iframe instructions

    """,
    'category': 'Custom Development',
    'depends': ['survey', 'mrp_workorder', 'mrp_plm', 'quality', 'quality_control', 'mrp'],
    'data': [
        # security
        # views
        'views/quality_views.xml',
        'views/mrp_workorder_view.xml',
        'views/backend_assets.xml',
        # data

    ],
    'demo': [],
    'qweb': ['static/src/xml/quality.xml'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
