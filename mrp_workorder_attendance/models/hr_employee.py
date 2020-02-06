
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


import logging
_logger = logging.getLogger(__name__)




class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def workorder_to_checkin(self, wo_id):
        action_date = fields.Datetime.now()
        for employee in self:
            if employee.attendance_state != 'checked_in':
                vals = {
                    'employee_id': employee.id,
                    'check_in': action_date,
                    'wo_id': wo_id
                }
                self.env['hr.attendance'].create(vals)
            else:
                attendance = self.env['hr.attendance'].search([('employee_id','=',employee.id),('check_out','=', False)], limit=1)
                raise UserError("%s (%s) is working in %s, %s." %(employee.name, employee.barcode, attendance.wo_id.name, attendance.wo_id.production_id.name))
    @api.multi
    def workorder_to_checkout(self, wo_id):
        action_date = fields.Datetime.now()
        for employee in self:
            attendance = self.env['hr.attendance'].search([('employee_id', '=', employee.id), ('check_out', '=', False), ('wo_id', '=', wo_id)], limit=1)
            if attendance:
                attendance.check_out = action_date
            else:
                _logger.warn('Cannot perform check out on %s #%s. workorder %s.' %(employee.name, employee.id, wo_id))

