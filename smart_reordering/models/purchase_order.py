
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    responsible_moves = fields.Many2many(
        comodel_name='stock.move',
        relation='rfq_responsible_move_rel',
        column1='move_id',
        column2='order_id'
    )

    @api.multi
    def return_responsible_action(self):
        action = self.env.ref('stock.stock_move_action').read()[0]
        action.update({
            'domain': [('id', 'in', self.responsible_moves.ids)],
            'context': {}
        })
        return action

    @api.multi
    def button_cancel(self):
        self.write({'responsible_moves': [(6, False, [])]})
        super(PurchaseOrder, self).button_cancel()

