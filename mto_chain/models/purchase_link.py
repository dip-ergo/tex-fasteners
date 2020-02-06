
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class PoMoLink(models.Model):
    _name = 'procurement.linking'
    _description = u'Procurement Raw Material Consumption Linking'
    _rec_name = 'purchase_id'

    purchase_id = fields.Many2one(string=u'Purchase',comodel_name='purchase.order',ondelete='set null')
    line_ids = fields.One2many(comodel_name='procurement.linking.line',inverse_name='linking_id',)
    linked = fields.Boolean(default=False)
    

    @api.multi
    def link_manual_procurement(self):
        for linking in self:
            for line in linking.line_ids.filtered(lambda line: not line.from_stock):
                parent_record = line.production_id if line.production_id else line.sale_id
                if not parent_record.node_id:
                    parent_record.node_id = parent_record.node_id.create({})
                    parent_record.node_id._set_ref(parent_record)
                if not line.purchase_line_id.node_id:
                    line.purchase_line_id.node_id = line.purchase_line_id.node_id.create({})
                    line.purchase_line_id.node_id._set_ref(line.purchase_line_id)
                parent_record.node_id.write({
                    'child_ids': [(4, line.purchase_line_id.node_id.id, False)]
                })
                moves = line.production_id.move_raw_ids.filtered(lambda m: m.product_id == line.purchase_line_id.product_id) if line.production_id else line.sale_id.move_ids
                for move in moves:
                    while(move.move_orig_ids):
                        move=move.move_orig_ids
                    move.created_purchase_line_id = line.purchase_line_id
                    if line.purchase_line_id.move_ids:
                        move.move_orig_ids = line.purchase_line_id.move_ids
            linking.linked = True

class PoMoLinkingLine(models.Model):
    _name = 'procurement.linking.line'
    _description = u'Procurement Raw Material Consumption Linking Line'

    linking_id = fields.Many2one(comodel_name='procurement.linking',ondelete='set null')    
    purchase_line_id = fields.Many2one(string=u'Purchase',comodel_name='purchase.order.line',ondelete='set null')
    production_id = fields.Many2one(string=u'Production',comodel_name='mrp.production',ondelete='set null')
    sale_id = fields.Many2one(string=u'Sale Line',comodel_name='sale.order.line',ondelete='set null')
    supply_quantity = fields.Float(related='purchase_line_id.product_qty', string="Supply Quantity")
    supply_uom = fields.Many2one(string=u'Supply Unit',comodel_name='uom.uom',related='purchase_line_id.product_uom')
    demand_quantity = fields.Float(string="Demand Quantity", compute='_get_demand')
    demand_uom = fields.Many2one(string=u'Demand Unit',comodel_name='uom.uom',compute='_get_demand')
    from_stock = fields.Boolean(readonly=True)
    source = fields.Char(compute='_get_source')

    def _get_source(self):
        for record in self:
            if record.production_id.node_id:
                record.source = record.production_id.node_id._get_parent().record_ref.display_name


    def _get_demand(self):
        for record in self:
            moves = False
            demand_quantity = 0
            if record.purchase_line_id and record.production_id:
                moves = record.production_id.move_raw_ids.filtered(lambda m: m.product_id == record.purchase_line_id.product_id).mapped('move_orig_ids')
            elif record.purchase_line_id and record.sale_id:
                moves = record.sale_id.move_ids.mapped('move_orig_ids')
            if moves:
                record.demand_quantity = sum(moves.mapped('product_uom_qty')) - sum(moves.mapped('reserved_availability'))
                record.demand_uom = moves.mapped('product_uom')

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    def link_manufactures(self):
        return {
            'name': _('Link Manufactures'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'procurement.linking',
            'context': {
                'default_purchase_line_id': self.id,
                'default_purchase_id': self.order_id.id,
            }
        }
        
class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def link_purchases(self):
        return {
            'name': _('Link Procurements'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'procurement.linking',
            'context': {
                'default_production_id': self.id
            }
        }