from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError

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

    # @api.multi
    # def open_produce_product(self):
    #     for raw_id in self.move_raw_ids:
    #         if raw_id.product_uom_qty > raw_id.reserved_availability:
    #             raise ValidationError(_('You are allowed to continue because there is not enough quantity in stock'))
    #     return super(MRpProduction,self).open_produce_product()

class MRPProductProduce(models.TransientModel):
    _inherit = 'mrp.product.produce'

    @api.multi
    def do_produce(self):
        if not all(self.produce_line_ids.mapped('qty_done')):
            raise UserError(_('You are not allowed to continue because there is a quantity = 0.'))
        return super(MRPProductProduce, self).do_produce()

