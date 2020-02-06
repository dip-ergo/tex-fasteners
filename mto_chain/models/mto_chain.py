
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)


class MTOChain(models.Model):
    _name = 'mto.chain'
    _description = u'MTO Chain'

    _rec_name = 'name'
    _order = 'res_model ASC, res_id ASC'

    
    name = fields.Char()
    res_model = fields.Char()
    res_id = fields.Integer()
    record_ref = fields.Reference(selection=[('purchase.order.line', 'Purchase Order'), ('mrp.production', 'Manufacturing Order'), ('sale.order.line', 'Sale Order Line')],
                                  compute='_get_ref',
                                  store=True)

    priority_id = fields.Many2one(comodel_name='mto.priority', ondelete='restrict')

    parent_ids = fields.Many2many(
        string=u'Parents',
        comodel_name='mto.chain',
        relation='mto_parent_child_rel',
        column1='parent_id',
        column2='child_id',
    )

    child_ids = fields.Many2many(
        string=u'Childs',
        comodel_name='mto.chain',
        relation='mto_parent_child_rel',
        column2='parent_id',
        column1='child_id',
    )

    @api.depends('res_model', 'res_id')
    def _get_ref(self):
        for participant in self:
            if participant.res_model:
                participant.record_ref = '%s,%s' % (
                    participant.res_model, participant.res_id or 0)

    @api.multi
    def _set_ref(self, record):
        self.ensure_one()
        record.ensure_one()
        self.write({'res_model': record._name, 'res_id': record.id, 'name': record.name})

    @api.model
    def get_html(self):
        result = {}
        rcontext = {}
        context = dict(self.env.context)
        active_id = context.get('active_id', False)
        active_model = context.get('model', False)
        if active_id and active_model:
            rcontext['node_id'] = self.env[active_model].browse(
                active_id).node_id
            result['html'] = self.env.ref(
                'mto_chain.mto_cascade_view').render(rcontext)

            rcontext['so_parent_date'] = "Date Discrepancy Report " +self.env['mto.discrepancy.report'].get_so_information(active_id)
            rcontext['so_parent_q'] = "Quantity Discrepancy Report " + self.env['mto.discrepancy.report'].get_so_information(active_id)
            rcontext['lines'] = self.env['mto.discrepancy.report'].get_so_line_discrepancy_report("date",active_id)
            rcontext['lines'] = sorted(rcontext['lines'], key=lambda i: (i['discrepancy_start_status'], i['discrepancy_finish_status']),reverse=True)
            rcontext['qlines'] = self.env['mto.discrepancy.report'].get_so_line_discrepancy_report("quantity",active_id)
            rcontext['qlines'] = sorted(rcontext['qlines'], key=lambda i: i['discrepancy_status'],reverse=True)
            # _logger.info(rcontext['lines'])
            result['date_html'] = self.env.ref('syray_discrepancy_report.report_discrepancy_view').render(rcontext)
            result['quantity_html'] = self.env.ref('syray_discrepancy_report.report_discrepancy_view_quantity').render(
                rcontext)

            # discrepancy['html'] = self.env['mto.discrepancy.report'].get_html()
            result['html'] = result['html'] + result['date_html'] + result['quantity_html']
        return result

    @api.model
    def _get_parent(self):
        self.ensure_one()
        node = self
        while (node.parent_ids):
            node = node.parent_ids
            if len(node) > 1:
                node = False
        return node

    @api.model
    def action_date_update(self, start_date=False, end_date=False):
        self.ensure_one()
        start_date, end_date = self.record_ref.do_date_update(start_date, end_date)
        if end_date and self.child_ids:
            for child in self.child_ids:
                child.action_date_update(end_date=end_date)
        if start_date and self.parent_ids:
            for parent in self.parent_ids:
                parent.action_date_update(start_date=start_date)

    @api.model
    def action_priority_update(self):
        self.ensure_one()
        if self.child_ids:
            self.child_ids.write({
                'priority_id': self.priority_id.id
            })
            for child in self.child_ids:
                child.action_priority_update()

    @api.model
    def action_cancel_mto(self):
        self.ensure_one()
        if self.res_model == 'mrp.production' and self.record_ref.state not in ('done', 'cancel'):
            self.record_ref.force_action_cancel()
        if self.child_ids:
            for child in self.child_ids:
                child.action_cancel_mto()
    


    @api.model
    def action_mo_plan(self):
        if self.res_model == 'mrp.production':
            self.record_ref.button_plan()
        if self.child_ids:
            for child in self.child_ids:
                child.action_mo_plan()

    @api.model
    def action_mo_unplan(self):
        if self.res_model == 'mrp.production':
            self.record_ref.button_unplan()
        if self.child_ids:
            for child in self.child_ids:
                child.action_mo_unplan()

    def get_childs(self):
        current = self
        records = self
        while(current.mapped('child_ids')):
            current = current.mapped('child_ids')
            records += current
        return records

class MTOChainMixin(models.AbstractModel):
    _name = 'mto.chain.mixin'

    node_id = fields.Many2one(
        comodel_name='mto.chain',
        ondelete='set null')

    priority_id = fields.Many2one(string='MTO Priority',
        comodel_name='mto.priority', ondelete='set null', related="node_id.priority_id", readonly=False, store=True)
    color = fields.Char(related='priority_id.color')

    @api.multi
    def action_update(self):
        for record in self:
            record.node_id.action_date_update()
            record.node_id.action_priority_update()

    @api.model
    def create(self, values):
        node_id = self.node_id.create({}).id
        values.update({'node_id': node_id})
        if not values.get('priority_id', False):
            priority_id = self.env['mto.priority'].search([], order='sequence DESC', limit=1).id
            values.update({'priority_id': priority_id})
        result = super(MTOChainMixin, self).create(values)
        result.node_id._set_ref(result)
        return result


class PlanUnplanWizard(models.TransientModel):
    _name = 'plan.unplan.wizard'
    _description = u'Plan Unplan Wizard'

    
    function = fields.Char()
    
    @api.multi
    def action_plan(self):
        context = dict(self.env.context)
        active_id = context.get('active_id', False)
        active_model = context.get('model', False)
        function = context.get('default_function', False)
        if active_id and active_model:
            node_id = self.env[active_model].browse(active_id).node_id
            if node_id and function:
                getattr(node_id, function)()
        return True