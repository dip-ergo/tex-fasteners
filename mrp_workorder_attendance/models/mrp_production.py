# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class MRPProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def force_action_cancel(self):
        for wo in self.mapped('workorder_ids').filtered(lambda wo: wo.state == 'progress'):
            wo.check_ids.unlink()
            wo.active_move_line_ids.unlink()
            timeline = self.env['mrp.workcenter.productivity'].search([('workorder_id','=',wo.id)])
            wo.action_cancel()
            if timeline:
                timeline.unlink()
        documents = {}
        for production in self:
            for move_raw_id in production.move_raw_ids.filtered(lambda m: m.state not in ('done', 'cancel')):
                iterate_key = self._get_document_iterate_key(move_raw_id)
                if iterate_key:
                    document = self.env['stock.picking']._log_activity_get_documents({move_raw_id: (move_raw_id.product_uom_qty, 0)}, iterate_key, 'UP')
                    for key, value in document.items():
                        if documents.get(key):
                            documents[key] += [value]
                        else:
                            documents[key] = [value]
            production.workorder_ids.filtered(lambda x: x.state not in ('cancel','done')).action_cancel()
            finish_moves = production.move_finished_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            raw_moves = production.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            (finish_moves | raw_moves)._do_unreserve()
            (finish_moves | raw_moves)._action_cancel()
            picking_ids = production.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            picking_ids.action_cancel()
        self.write({'state': 'cancel', 'is_locked': True})
        if documents:
            filtered_documents = {}
            for (parent, responsible), rendering_context in documents.items():
                if not parent or parent._name == 'stock.picking' and parent.state == 'cancel' or parent == self:
                    continue
                filtered_documents[(parent, responsible)] = rendering_context
            self._log_manufacture_exception(filtered_documents, cancel=True)
        return True

    def _cal_price(self, consumed_moves):
        """Set a price unit on the finished move according to `consumed_moves`.
        """
        super(MRPProduction, self)._cal_price(consumed_moves)
        worker_cost = 0
        finished_move = self.move_finished_ids.filtered(lambda x: x.product_id == self.product_id and x.state not in ('done', 'cancel') and x.quantity_done > 0)
        if finished_move:
            finished_move.ensure_one()
            for work_order in self.workorder_ids:
                duration = sum(work_order.worker_times.mapped('worked_hours'))
                worker_cost += duration * work_order.workcenter_id.cost_hour_employee
            if finished_move.product_id.cost_method in ('fifo', 'average'):
                qty_done = finished_move.product_uom._compute_quantity(finished_move.quantity_done, finished_move.product_id.uom_id)
                finished_move.price_unit += (worker_cost/ qty_done)
                finished_move.value += worker_cost
        return True