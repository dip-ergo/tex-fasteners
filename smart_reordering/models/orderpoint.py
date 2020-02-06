
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError



class StockReorder(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    
    qty_multiple = fields.Float(compute='_get_qty_multiple')

    def _get_qty_multiple(self):
        for record in self:
            record.qty_multiple = record.product_id.selected_vendor_id.min_qty