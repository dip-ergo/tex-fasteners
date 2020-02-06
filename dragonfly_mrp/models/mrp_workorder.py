# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields, _
from werkzeug import url_encode


class MRPWorkorder(models.Model):
    _inherit = "mrp.workorder"

    public_url = fields.Char(related="current_quality_check_id.public_url")

    @api.multi
    def action_open_documents(self):
        self.ensure_one()
        url = '/web#%s' % url_encode({'action': 'dragonfly_mrp.action_open_active_workorder', 'active_id': self.id})
        return {
            'type': 'ir.actions.act_url',
            'name': _("Product Documents"),
            'target': '_blank',
            'url': url,
        }

    @api.model
    def open_product_attachments(self):
        workorder = self.browse(self.env.context.get('active_id')).exists()
        return workorder.product_id.action_see_attachments()
