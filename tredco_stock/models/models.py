# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockPickingCT(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def button_validate(self):
        self.ensure_one()
        if self.picking_type_code != 'incoming' and not all(self.move_ids_without_package.mapped('quantity_done')):
            raise UserError(_('You are not allowed to continue because there is a quantity = 0.'))
        return super(StockPickingCT, self).button_validate()