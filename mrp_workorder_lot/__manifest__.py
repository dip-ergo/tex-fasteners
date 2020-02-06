# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Syncoria WO Lot',
    'summary': 'Syncoria WO Lot Number Selection',
    'website': 'http://www.ergo-ventures.com',
    'version': '1.0',
    'author': 'Ergo Ventures Ltd.',
    'description': """
WO Documents
===============

* [1938284]
    -  This will fetch the lot number from related Picking and show them in Lot number dropdown selection also Add/Edit button removed from selection wizard.
    """,
    'category': 'Custom Development',
    'depends': ['dragonfly_mrp','stock'],
    'data': [
        # security
        # views
        'views/mrp_workorder_lot_selection.xml',
        # data

    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
