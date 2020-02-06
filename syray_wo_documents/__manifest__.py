# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Syncoria WO Documents',
    'summary': 'Syncoria WO Documents Enhancement',
    'website': 'http://www.ergo-ventures.com',
    'version': '1.0',
    'author': 'Ergo Ventures Ltd.',
    'description': """
WO Documents
===============

* [1938284]
    -  This will add a button ('Documents') on the work order process screen that will open a new popup with the attachment screen of the product
       that is selected on the related manufacturing order.

    """,
    'category': 'Custom Development',
    'depends': ['dragonfly_mrp','stock','mrp_workorder_attendance'],
    'data': [
        # security
        # views
        'views/mrp_workorder_document_view.xml',
        'views/syray_attachment_wizard_view.xml',
        'views/mrp_document_syray.xml',
        'views/backend_assets.xml',
        # data

    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
