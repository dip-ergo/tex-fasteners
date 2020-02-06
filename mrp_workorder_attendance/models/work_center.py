
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError



class WorkCenter(models.Model):
    _inherit = 'mrp.workcenter'

    cost_hour_employee = fields.Float(string='Cost per hour per employee', help='Specify cost of work center per hour per employee.', default=0.0)
 

