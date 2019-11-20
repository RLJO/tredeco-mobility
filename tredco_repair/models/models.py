# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError

class TredcoRepair(models.Model):
    _inherit = 'repair.order'

    def action_validate(self):
        self.ensure_one()
        if not all(self.operations.mapped('product_uom_qty')):
            raise UserError(_('You are not allowed to continue because there is a quantity = 0.'))
        for operation in self.operations:
            stock_trace_obj = self.env['stock.traceability.report']
            lines = stock_trace_obj.get_lines(model_id=operation.lot_id.id,model_name='stock.production.lot',level=1)
            if lines:
                for line in lines:
                    if line['usage'] == 'out':
                        out_qty=out_qty+1
                    elif line['usage'] == 'in':
                        in_qty=in_qty+1
                available_qty = in_qty - out_qty
                if operation.product_uom_qty > available_qty:
                    raise ValidationError(_('You are allowed to continue because there is not enough quantity in lot'))
            elif operation.lot_id.product_qty < operation.product_uom_qty:
                raise ValidationError(_('You are allowed to continue because there is not enough quantity in lot'))
        return super(TredcoRepair, self).action_validate()

