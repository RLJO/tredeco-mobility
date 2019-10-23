from odoo import models, fields, api

class MRpProduction(models.Model):
    _inherit = 'mrp.production'

    def do_un_produce(self):
        # Unlink the moves related to manufacture order
        moves = self.env['stock.move.line'].search([('reference', '=', self.name)]).unlink()
        self.state ='confirmed'


