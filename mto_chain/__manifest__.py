# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Syncoria MTO Chain',
    'summary': 'Syncoria Make to Order Chain',
    'website': 'http://www.ergo-ventures.com',
    'version': '1.0',
    'author': 'Ergo Ventures Ltd.',
    'description': """
    """,
    'category': 'Custom Development',
    'depends': ['mrp','stock','sale','purchase','web_tree_dynamic_colored_field'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/mto.priority.csv',
        'views/mto_chain_view.xml',
        'views/cancel_mto.xml',
        'views/sale_order.xml',
        'views/procurement_linking_wizard.xml',
        'views/mrp_production.xml',
        'views/stock_move.xml',
        'views/mto_priority.xml',
        'views/purchase_order.xml'
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
