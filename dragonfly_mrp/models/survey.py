# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SurveyUserInput(models.Model):
    """ Metadata for a set of one user's answers to a particular survey """

    _inherit = "survey.user_input"

    quality_check_id = fields.Many2one("quality.check", string="Quality Check")
