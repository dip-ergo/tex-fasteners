# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class QualityPoint(models.Model):
    _inherit = "quality.point"

    survey_template_id = fields.Many2one('survey.survey', string="Quality Check Survey Template")
    public_url = fields.Char(related="survey_template_id.public_url")

    # @api.onchange('user_id', 'survey_template_id')
    # def onchange_set_token(self):
    #     public_url = self.survey_template_id and self.survey_template_id.public_url or ''
    #     if self.user_id and self.survey_template_id:
    #         user_input = self.survey_template_id.user_input_ids.filtered(lambda r: r.partner_id == self.user_id.partner_id)
    #         public_url += user_input and '/' + user_input[0].token or ''
    #     self.public_url = public_url


class QualityCheck(models.Model):
    _inherit = "quality.check"

    public_url = fields.Char("public_url")

    def create_survey_user_input(self, survey_template_id, user_id):
        self.ensure_one()
        UserInput = self.env['survey.user_input']
        if survey_template_id and user_id:
            UserInput = UserInput.create({
                                'survey_id': survey_template_id.id,
                                'partner_id': user_id.partner_id.id,
                                'quality_check_id': self.id,
                                'type': 'link',
                            })
            public_url = '%s/%s' % (survey_template_id.public_url, UserInput.token)
            self.write({'public_url': public_url})
        return UserInput

    @api.model
    def create(self, vals):
        rec = super(QualityCheck, self).create(vals)
        if rec.point_id and rec.point_id.survey_template_id and rec.point_id.user_id:
            rec.create_survey_user_input(rec.point_id.survey_template_id, rec.point_id.user_id)
        return rec
