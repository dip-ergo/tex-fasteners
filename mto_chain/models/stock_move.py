
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta


class StockMove(models.Model):
    _inherit = 'stock.move'

    raw_mto_parent = fields.Many2one(
        string=u'MTO Parent',
        comodel_name='sale.order.line',
        compute='_compute_mto_parent',
    )
    raw_mto_parent_location = fields.Many2one(
        string=u'Parent Location',
        comodel_name='stock.location',
        compute='_compute_mto_parent',
    )
    
    

    @api.depends('raw_material_production_id')
    def _compute_mto_parent(self):
        for move in self:
            origin_move = move
            while move:
                production = move.raw_material_production_id
                sale = move.sale_line_id
                if production:
                    if production.node_id:
                        raw_mto_parent = production.node_id._get_parent()
                        if raw_mto_parent.res_model == 'sale.order.line':
                            origin_move.raw_mto_parent = raw_mto_parent.record_ref
                            origin_move.raw_mto_parent_location = raw_mto_parent.record_ref.order_id.sub_location_id
                    break
                elif sale:
                    origin_move.raw_mto_parent = sale
                    origin_move.raw_mto_parent_location = sale.order_id.sub_location_id
                    break
                else:
                    move = move.move_dest_ids[0] if move.move_dest_ids else False
    
    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        return [
            'product_id', 'price_unit', 'product_packaging', 'procure_method',
            'product_uom', 'restrict_partner_id', 'scrapped', 'origin_returned_move_id',
            'package_level_id','move_orig_ids','move_dest_ids'
        ]
    
    def move_date_update(self, date, sale_id):
        moves = self.filtered(lambda m: m.state not in ('draft','cancel','done') and m.picking_id.sale_id == sale_id)
        moves.write({
            'date': date,
            'date_expected': date
        })
        if moves:
            for move in moves:
                if move.move_orig_ids:
                    move.move_orig_ids.move_date_update(date, sale_id)