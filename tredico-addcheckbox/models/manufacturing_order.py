
from odoo import api, fields, models,_

from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_round, float_compare, float_is_zero



# class StockQuant(models.Model):
#     _inherit = 'stock.quant'
#
#     @api.constrains('quantity')
#     def check_quantity(self):
#         for quant in self:
#             if float_compare(quant.quantity, 1,
#                              precision_rounding=quant.product_uom_id.rounding) > 0 and quant.lot_id and quant.product_id.tracking == 'serial':
#                 print('hello')
#                 # raise ValidationError(_('A serial number should only be linked to a single product.'))


class addcheckbox(models.Model):
    _inherit = "stock.move.line"
    def unlink(self):
        print('unlink')
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
        # moves = self.mapped('move_id')
        # res = super(addcheckbox, self).unlink()
        # # if moves:
        # #     moves._recompute_state()
        # return res


    chick_box= fields.Boolean(string="update Stock" )

class add_checkbox(models.Model):
    _inherit = "mrp.production"
    check_box = fields.Boolean(string="Post Singl Lines?")
    @api.onchange('finished_move_line_ids')
    def get_check_value(self):
        for item in self:
            for line in item.finished_move_line_ids:
                if line.chick_box==True:
                    item.check_box=True

    @api.multi
    def post_inventory(self):
        if self.check_box == True:
            print('if')
            for order in self:
                # moves_to_do = order.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel'))

                products_finished = order.finished_move_line_ids.filtered(lambda x:x.chick_box == True)
                if products_finished:
                    for item in products_finished:

                        if item.state !='done' and item.state != 'cancel':

                                stock_quatity=self.env['stock.quant'].search([('product_id','=',item.product_id.id)],limit=1)

                                for product in stock_quatity:
                                    if item.product_id.id== product.product_id.id:
                                        print('product name', item.product_id.name)
                                        print('serial number of finished', item.lot_id.id)
                                        print('serial of actual product',product.lot_id.id)

                                        # product.sudo().create({
                                        #     'product_id': product.product_id.id,
                                        #     'location_id': product.location_id.id,
                                        #     'quantity': product.quantity + item.qty_done,
                                        #     'reserved_quantity': item.qty_done,
                                        #     'lot_id': item.lot_id.id,
                                        #     'product_uom_id': product.product_uom_id.id,
                                        #
                                        # })
                                        product.sudo().write({
                                            'quantity' :product.quantity +item.qty_done,
                                        })
                                        item.state = 'done'
                                for row in order.move_raw_ids:
                                    stock_move_id = self.env['stock.move'].search([('product_id', '=', row.product_id.id)])

                                    stock_product_id = self.env['stock.quant'].search([('product_id', '=', row.product_id.id)])
                                    for consum in stock_product_id:

                                        if consum.product_id.id == row.product_id.id:

                                            total_first = row.product_uom_qty / order.product_qty

                                            total = total_first * item.qty_done

                                            consum.sudo().write({
                                                'quantity': consum.quantity - total,
                                            })
                                    for rec in stock_move_id:

                                                if row.state != 'done':
                                                    row.state = 'done'




        else:
            print('else')

            for order in self:

                    moves_not_to_do = order.move_raw_ids.filtered(lambda x: x.state == 'done')
                    moves_to_do = order.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
                    for move in moves_to_do.filtered(lambda m: m.product_qty == 0.0 and m.quantity_done > 0):
                        move.product_uom_qty = move.quantity_done
                    moves_to_do._action_done()
                    moves_to_do = order.move_raw_ids.filtered(lambda x: x.state == 'done') - moves_not_to_do
                    order._cal_price(moves_to_do)
                    moves_to_finish = order.move_finished_ids.filtered(lambda x: (x.state not in ('done', 'cancel')) )
                    moves_to_finish._action_done()
                    # order.action_assign()
                    consume_move_lines = moves_to_do.mapped('active_move_line_ids')
                    for moveline in moves_to_finish.mapped('active_move_line_ids'):

                            if moveline.product_id == order.product_id and moveline.move_id.has_tracking != 'none':
                            #     if any([not ml.lot_produced_id for ml in consume_move_lines]):
                            #         raise UserError(_('You can not consume without telling for which lot you consumed it'))
                                # Link all movelines in the consumed with same lot_produced_id false or the correct lot_produced_id
                                filtered_lines = consume_move_lines.filtered(lambda x: (x.lot_produced_id == moveline.lot_id) and (moveline.chick_box == True))
                                moveline.write({'consume_line_ids': [(6, 0, [x for x in filtered_lines.ids])]})
                                print(moveline)
                                print(moveline.lot_id)
                                print(filtered_lines)
                            else:
                                # Link with everything
                                moveline.write({'consume_line_ids': [(6, 0, [x for x in consume_move_lines.ids])]})


        return True
