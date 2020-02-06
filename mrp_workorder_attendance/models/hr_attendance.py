# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    wo_id = fields.Many2one(string=u'Work Order', comodel_name='mrp.workorder', ondelete='set null')

    wc_id = fields.Many2one(string=u'Work Center', related='wo_id.workcenter_id', store=True)

    @api.multi
    def save(self):
        return {'type': 'ir.actions.act_window_close'}
        