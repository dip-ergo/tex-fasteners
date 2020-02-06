
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class MTOPriority(models.Model):
    _name = 'mto.priority'
    _description = u'MTO Priority'

    _rec_name = 'name'
    _order = 'sequence'

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    color = fields.Char()
