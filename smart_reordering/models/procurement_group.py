
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta


class ProcurementGroup(models.Model):
    _inherit='procurement.group'

    @api.model
    def _procurement_from_orderpoint_get_grouping_key(self, orderpoint_ids):
        orderpoints = self.env['stock.warehouse.orderpoint'].browse(orderpoint_ids)
        return (orderpoints.id, orderpoints.location_id.id)

    @api.model
    def _procurement_from_orderpoint_get_groups(self, orderpoint_ids):
        OrderPoint = self.env['stock.warehouse.orderpoint'].browse(orderpoint_ids)
        lead_days = OrderPoint.product_id.reorder_lead_days
        to_date = fields.Datetime.now() + relativedelta(days=+lead_days)
        return [{'to_date': to_date, 'procurement_values': dict()}]
