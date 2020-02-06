
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero
from datetime import datetime, timedelta


class SaleOrderLine(models.Model):
    _name = 'sale.order.line'

    _inherit = ['sale.order.line', 'mto.chain.mixin']

    date_expected = fields.Datetime('Delivery Date')

    @api.model
    def default_get(self, fields):
        res = super(SaleOrderLine, self).default_get(fields)
        res['priority_id'] = self.env['mto.priority'].search([], limit=1).id
        return res

    @api.model
    def do_date_update(self, start_date=False, end_date=False):
        self.ensure_one()
        if end_date:
            start_date = end_date - timedelta(days=self.product_id.sale_delay)
            return_date = False, start_date
        elif start_date:
            end_date = start_date + timedelta(days=self.product_id.sale_delay)
            return_date = end_date, False
        elif not any((end_date,start_date)):
            start_date = self.date_expected - timedelta(days=self.product_id.sale_delay)
            end_date = self.date_expected
            return_date = end_date, start_date
        
        if self.state not in ('done', 'cancel'):
            self.write({
                'date_expected': end_date
            })
            if self.move_ids:
                for move in self.move_ids:
                    move.move_date_update(start_date, move.sale_line_id.order_id)
        return return_date

class PurchaseOrder(models.Model):
    _name = 'purchase.order.line'

    _inherit = ['purchase.order.line', 'mto.chain.mixin']

    @api.model
    def do_date_update(self, start_date=False, end_date=False):
        return False, False

    def name_get(self):
        return [(record.id, '%s / %s'%(record.order_id.name, record.product_id.name)) for record in self]


class MrpProduction(models.Model):
    _name = 'mrp.production'

    _inherit = ['mrp.production', 'mto.chain.mixin']

    def _get_start_date(self):
        return max(self.date_planned_start, datetime.now())

    @api.model
    def do_date_update(self, start_date=False, end_date=False):
        self.ensure_one()
        if end_date:
            start_date = end_date - timedelta(days=self.product_id.produce_delay)
            return_date = False, start_date
        elif start_date:
            end_date = start_date + timedelta(days=self.product_id.produce_delay)
            return_date = end_date, False
        elif not any((end_date,start_date)):
            start_date = self.date_planned_start
            end_date = self.date_planned_finished
            return_date = end_date, start_date
        
        if self.state not in ('done', 'cancel', 'progress'):
            self.write({
                'date_planned_start': start_date,
                'date_planned_finished': end_date
            })
            self.picking_ids.mapped('move_lines').write({
                'date': start_date,
                'date_expected': start_date
            })
            self.move_finished_ids.write({
                'date': end_date,
                'date_expected': end_date
            })
            self.move_raw_ids.write({
                'date': start_date,
                'date_expected': start_date
            })
        return return_date


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _action_confirm(self):
        super(SaleOrder, self)._action_confirm()
        for order in self:
            for line in order.order_line:
                line.node_id.action_date_update()
                line.node_id.action_priority_update()
    
    @api.multi
    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        self.mapped('order_line').mapped('node_id').write({
                'parent_ids': [(6, False, [])],
                'child_ids': [(6, False, [])]
            })
        return res