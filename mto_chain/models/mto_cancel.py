
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError



class CancelMTO(models.TransientModel):
    _name = 'cancel.mto.wizard'

    @api.multi
    def action_cancel(self):
        active_model = self.env.context.get('active_model', False)
        active_id = self.env.context.get('active_id', False)
        sale_line = self.env[active_model].browse(active_id)
        if sale_line.node_id and sale_line.product_uom_qty:
            sale_line.node_id.action_cancel_mto()
            sale_line.product_uom_qty = 0