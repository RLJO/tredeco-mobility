from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError
from odoo.addons import decimal_precision as dp
from odoo.tools.pycompat import izip
from odoo.tools.float_utils import float_round, float_compare, float_is_zero

# class StockMoveLines(models.Model):
#     _name = 'stock.move.line.unlink'
#     _inherit = 'stock.move.line'


class MRpProduction(models.Model):
    _inherit = 'mrp.production'


    show_quality_checks_and_alerts = fields.Boolean(compute='check_quantity')

    def do_un_produce(self):
        moves = self.env['stock.move.line'].search([('reference', '=', self.name)]).unlink()

        self.state = 'confirmed'

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
        # for raw_id in self.move_raw_ids:
            # if raw_id.product_uom_qty > raw_id.reserved_availability:
            #     raise ValidationError(_('You are allowed to continue because there is not enough quantity in stock'))
        return super(MRpProduction,self).open_produce_product()

class MRPProductProduce(models.TransientModel):
    _inherit = 'mrp.product.produce'

    @api.multi
    def do_produce(self):
        if not all(self.produce_line_ids.mapped('qty_done')):
            raise UserError(_('You are not allowed to continue because there is a quantity = 0.'))
        return super(MRPProductProduce, self).do_produce()

# class addcheckbox(models.Model):
#     _inherit = "stock.move.line"
#
#     chick_box= fields.Boolean(string="Check Box" )
#
# class add_checkbox(models.Model):
#     _inherit = "mrp.production"
#
#     @api.multi
#     def post_inventory(self):
#
#         for order in self:
#
#             moves_not_to_do = order.move_raw_ids.filtered(lambda x: x.state == 'done')
#             moves_to_do = order.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
#             for move in moves_to_do.filtered(lambda m: m.product_qty == 0.0 and m.quantity_done > 0):
#                 move.product_uom_qty = move.quantity_done
#             moves_to_do._action_done()
#             moves_to_do = order.move_raw_ids.filtered(lambda x: x.state == 'done') - moves_not_to_do
#             order._cal_price(moves_to_do)
#             moves_to_finish = order.move_finished_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
#             moves_to_finish._action_done()
#             order.action_assign()
#             consume_move_lines = moves_to_do.mapped('active_move_line_ids')
#             for moveline in moves_to_finish.mapped('active_move_line_ids'):
#                 if moveline.chick_box:
#                     if moveline.product_id == order.product_id and moveline.move_id.has_tracking != 'none':
#                         if any([not ml.lot_produced_id for ml in consume_move_lines]):
#                             raise UserError(_('You can not consume without telling for which lot you consumed it'))
#                         # Link all movelines in the consumed with same lot_produced_id false or the correct lot_produced_id
#                         filtered_lines = consume_move_lines.filtered(lambda x: x.lot_produced_id == moveline.lot_id)
#                         moveline.write({'consume_line_ids': [(6, 0, [x for x in filtered_lines.ids])]})
#                     else:
#                         # Link with everything
#                         moveline.write({'consume_line_ids': [(6, 0, [x for x in consume_move_lines.ids])]})
#
#         return True