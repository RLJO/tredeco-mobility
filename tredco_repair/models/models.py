# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class TredcoRepair(models.Model):
    _inherit = 'repair.order'

    def action_validate(self):
        self.ensure_one()
        if not all(self.operations.mapped('product_uom_qty')):
            raise UserError(_('You are not allowed to continue because there is a quantity = 0.'))
        return super(TredcoRepair, self).action_validate()

