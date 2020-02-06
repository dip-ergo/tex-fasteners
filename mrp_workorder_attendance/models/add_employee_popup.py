# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AddEmployeetoWorkorder(models.Model):
    _name = 'workorder.add.employee'
    _inherit = ['barcodes.barcode_events_mixin']
    _description = u'Adding employee to workorder module'

    _rec_name = 'wo_id'
    _order = 'wo_id ASC'

    wo_id = fields.Many2one(
        string=u'Workorder',
        comodel_name='mrp.workorder',
        ondelete='set null',
    )

    employee_ids = fields.Many2many(
        string=u'Employees',
        comodel_name='hr.employee',
        related='wo_id.employee_ids',
        readonly=False
        )

    def on_barcode_scanned(self, barcode):
        employee = self.env['hr.employee'].search([('barcode', '=', barcode)], limit=1)
        if employee:
            if employee.id not in self.employee_ids.ids:
                self.update({'employee_ids': [(4,employee.id, False)]})
            else:
                self.update({'employee_ids': [(3,employee.id, False)]})
                return {
                    'warning': {
                        'title': 'Worker Removed',
                        'message': '%s (%s) removed from workworder.' % (employee.name, employee.barcode)
                    }
                }
            