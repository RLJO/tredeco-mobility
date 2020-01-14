from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError
from odoo.addons import decimal_precision as dp
from odoo.tools.pycompat import izip
from odoo.tools.float_utils import float_round, float_compare, float_is_zero

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def unlink(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for ml in self:
            # if ml.state in ('done', 'cancel'):
            #     raise UserError(_('You can not delete product moves if the picking is done. You can only correct the done quantities.'))
            # Unlinking a move line should unreserve.
            if ml.product_id.type == 'product' and not ml.location_id.should_bypass_reservation() and not float_is_zero(ml.product_qty, precision_digits=precision):
                try:
                    self.env['stock.quant']._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
                except UserError:
                    if ml.lot_id:
                        self.env['stock.quant']._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty, lot_id=False, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
                    else:
                        raise
        moves = self.mapped('move_id')
        res = super(StockMoveLine, self).unlink()
        if moves:
            moves._recompute_state()
        return res
    
class MRpProduction(models.Model):
    _inherit = 'mrp.production'


    show_quality_checks_and_alerts = fields.Boolean(compute='check_quantity')

    def do_un_produce(self):
        # Unlink the moves related to manufacture order
        moves = self.env['stock.move.line'].search([('reference', '=', self.name)]).unlink()
        self.state ='confirmed'

    @api.multi
    def check_quantity(self):
        finished_product_quantity = sum(self.finished_move_line_ids.mapped('qty_done'))
        if finished_product_quantity == self.product_qty:
            self.show_quality_checks_and_alerts = True
        else:
            self.show_quality_checks_and_alerts = False

    def do_cancel(self):
        for finished_product in self.finished_move_line_ids:
            finished_product.state = 'draft'
        moves = self.env['stock.move.line'].search([('reference', '=', self.name)])
        for move in moves:
            move.state = 'draft'
        self.do_un_produce()
        self.state = 'cancel'
        return True

    @api.multi
    def open_produce_product(self):
        self.ensure_one()
        if not all(self.move_raw_ids.mapped('product_uom_qty')):
            raise UserError(_('You are not allowed to continue because there is a quantity = 0.'))
        return super(MRpProduction, self).open_produce_product()

    @api.multi
    def open_produce_product(self):
        for raw_id in self.move_raw_ids:
            if raw_id.product_uom_qty > raw_id.reserved_availability:
                raise ValidationError(_('You are allowed to continue because there is not enough quantity in stock'))
        return super(MRpProduction,self).open_produce_product()

class MRPProductProduce(models.TransientModel):
    _inherit = 'mrp.product.produce'

    @api.multi
    def do_produce(self):
        if not all(self.produce_line_ids.mapped('qty_done')):
            raise UserError(_('You are not allowed to continue because there is a quantity = 0.'))
        return super(MRPProductProduce, self).do_produce()

