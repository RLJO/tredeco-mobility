from odoo import models, fields, api

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