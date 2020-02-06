# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields
from odoo.exceptions import UserError
from odoo.tools import float_compare
from odoo import exceptions
from datetime import datetime
from collections import defaultdict
import logging
_logger = logging.getLogger(__name__)


class MRPLotFetch(models.Model):
    _inherit = "mrp.workorder"
    reserved_lot_ids = fields.Many2many('stock.production.lot', compute='_compute_reserved_lots')

    @api.depends('move_raw_ids','active_move_line_ids')
    def _compute_reserved_lots(self):
        reserved_lots = defaultdict(float)
        for wo in self:
            for raw_move in wo.move_raw_ids.filtered(lambda move: move.product_id == wo.component_id).mapped('active_move_line_ids'):
                reserved_lots[raw_move.lot_id.id] += raw_move.product_qty
            for move_line in wo.active_move_line_ids.filtered(lambda move: move.product_id == wo.component_id):
                if move_line.lot_id:
                    reserved_lots[move_line.lot_id.id] -= move_line.qty_done
            available_lots = [lot_id for lot_id,reserved_qty in reserved_lots.items() if float_compare(reserved_qty, 0, precision_digits=4) == 1]
            wo.update({'reserved_lot_ids': [(6, 0, available_lots)]})

    @api.onchange('lot_id')
    def get_lot_qty(self):
        if self.lot_id:
            reserved_qty = sum(self.move_raw_ids.mapped('active_move_line_ids').filtered(lambda line: line.lot_id == self.lot_id).mapped('product_qty'))
            used_qty = sum(self.active_move_line_ids.filtered(lambda line: line.lot_id == self.lot_id).mapped('qty_done'))
            self.qty_done = reserved_qty - used_qty

    def _next(self, state='pass'):
        """ This function:
        - first: fullfill related move line with right lot and validated quantity.
        - second: Generate new quality check for remaining quantity and link them to the original check.
        - third: Pass to the next check or return a failure message.
        """
        self.ensure_one()
        if self.qty_producing <= 0 or self.qty_producing > self.qty_remaining:
            raise UserError(_('Please ensure the quantity to produce is nonnegative and does not exceed the remaining quantity.'))
        elif self.test_type == 'register_consumed_materials':
            # Form validation
            if self.component_tracking != 'none' and not self.lot_id:
                raise UserError('LOT Number is incorrect. Please input again. If you see the error message again, please see Inventory/Warehouse Personnel.')
            if self.component_tracking == 'none' and self.qty_done <= 0:
                raise UserError(_('Please enter a positive quantity.'))

            self._update_active_move_line()

            self._create_subsequent_checks()

        if self.test_type == 'picture' and not self.picture:
            raise UserError(_('Please upload a picture.'))

        self.current_quality_check_id.write({
            'quality_state': state,
            'user_id': self.env.user.id,
            'control_date': datetime.now()})
        if self.skip_completed_checks:
            self._change_quality_check(increment=1, children=1, checks=self.skipped_check_ids)
        else:
            self._change_quality_check(increment=1, children=1)