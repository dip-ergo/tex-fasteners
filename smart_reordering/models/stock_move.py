
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    responsible_purchases = fields.Many2many(
        comodel_name='purchase.order',
        relation='rfq_responsible_move_rel',
        column2='move_id',
        column1='order_id'
    )
