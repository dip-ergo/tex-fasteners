# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields, _
from werkzeug import url_encode


class MRPWorkorder(models.Model):
    _inherit = "mrp.workorder"

    public_url = fields.Char(related="current_quality_check_id.public_url")

    @api.multi
    def action_open_documents_syray(self):
        self.ensure_one()
        # if context is None: context = {}
        # if context.get('active_model') != self._name:
        #     context.update(active_id=self.id, active_model=self._name)
        kanban_view = self.env.ref("syray_wo_documents.syray_product_attachment_wizard")
        return {
            'type': 'ir.actions.act_window',
            'name': _("Product Documents"),
            'res_model': 'mrp.document',
            'view_mode': 'kanban',
            'target' : 'new',
            'domain' : [
            '|',
            '&', ('res_model', '=', 'product.product'), ('res_id', '=', self.product_id.id),
            '&', ('res_model', '=', 'product.template'), ('res_id', '=', self.product_id.product_tmpl_id.id)],
            'views': [[kanban_view.id, "kanban"]],
            'context': self.env.context
        }

    @api.model
    def open_product_attachments_syray(self):
        workorder = self.browse(self.env.context.get('active_id')).exists()
        return workorder.product_id.action_see_attachments()


class MRPDocument(models.Model):
    _inherit = "mrp.document"

    @api.multi
    def open_attachment(self):
        form_view = self.env.ref("syray_wo_documents.syray_mrp_document_view")
        url = '/web#%s' % url_encode({'action': 'syray_wo_documents.mrp_doc_open_pdf', 'id': self.id, 'active_id': self.id, 'model': 'mrp.document'})
        # return {
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'mrp.document',
        #     'name': 'Record name',
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'res_id': self.id,
        #     'target': 'new',
        #     'views': [[form_view.id,"form"]]
        # }
        return {
            'type': 'ir.actions.act_url',
            'name': "Product Document",
            'target': '_blank',
            'context': {},
            'url': url,
        }