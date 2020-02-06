# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    worked_hour_threshold = fields.Float(related="company_id.manufacturing_worked_hour_threshold", readonly=False)
