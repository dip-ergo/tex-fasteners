
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError



class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    priority_id = fields.Many2one(
        comodel_name='mto.priority', ondelete='set null', related="production_id.priority_id", store=True)
    color = fields.Char(related='priority_id.color')
    released = fields.Boolean(related="production_id.released")

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    released = fields.Boolean(default=False, readonly=True)

    @api.multi
    def button_release(self):
        self.write({
            'released': True
        })
            
    @api.multi
    def button_unrelease(self):
        self.write({
            'released': False
        })

    def button_unplan(self):
        for production in self:
            production.button_unrelease()
        super(MrpProduction, self).button_unplan()
    
    def check_mto_progress(self):
        childs =  self.node_id.get_childs().filtered(lambda r: r.res_model == 'mrp.production')
        if not childs or all(childs.mapped('record_ref').mapped(lambda p: p.state not in ('progress', 'done'))):
            return True
        return False

    def action_cancel_with_mto(self):
        self.action_cancel()
        for production in self:
            if production.node_id:
                production.node_id.write({
                    'parent_ids': [(6, False, [])],
                    'child_ids': [(6, False, [])],
                })
