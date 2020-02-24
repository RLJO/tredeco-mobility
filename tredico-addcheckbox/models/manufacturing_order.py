
from odoo import api, fields, models,_

from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_round, float_compare, float_is_zero



class StockQuant(models.Model):
    _inherit = 'stock.quant'
    manufacturing_id=fields.Many2one('mrp.production')

    @api.model
    def _update_reserved_quantity(self, product_id, location_id, quantity, lot_id=None, package_id=None, owner_id=None,
                                  strict=False):
        """ Increase the reserved quantity, i.e. increase `reserved_quantity` for the set of quants
        sharing the combination of `product_id, location_id` if `strict` is set to False or sharing
        the *exact same characteristics* otherwise. Typically, this method is called when reserving
        a move or updating a reserved move line. When reserving a chained move, the strict flag
        should be enabled (to reserve exactly what was brought). When the move is MTS,it could take
        anything from the stock, so we disable the flag. When editing a move line, we naturally
        enable the flag, to reflect the reservation according to the edition.

        :return: a list of tuples (quant, quantity_reserved) showing on which quant the reservation
            was done and how much the system was able to reserve on it
        """
        self = self.sudo()
        rounding = product_id.uom_id.rounding
        quants = self._gather(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id,
                              strict=strict)
        reserved_quants = []

        if float_compare(quantity, 0, precision_rounding=rounding) > 0:
            # if we want to reserve
            available_quantity = self._get_available_quantity(product_id, location_id, lot_id=lot_id,
                                                              package_id=package_id, owner_id=owner_id, strict=strict)
            if float_compare(quantity, available_quantity, precision_rounding=rounding) > 0:
                raise UserError(_(
                    'It is not possible to reserve more products of %s than you have in stock.') % product_id.display_name)
        elif float_compare(quantity, 0, precision_rounding=rounding) < 0:
            # if we want to unreserve
            available_quantity = sum(quants.mapped('reserved_quantity'))
            # if float_compare(abs(quantity), available_quantity, precision_rounding=rounding) > 0:
            #     raise UserError(_(
            #         'It is not possible to unreserve more products of %s than you have in stock.') % product_id.display_name)
        else:
            return reserved_quants

        for quant in quants:
            if float_compare(quantity, 0, precision_rounding=rounding) > 0:
                max_quantity_on_quant = quant.quantity - quant.reserved_quantity
                if float_compare(max_quantity_on_quant, 0, precision_rounding=rounding) <= 0:
                    continue
                max_quantity_on_quant = min(max_quantity_on_quant, quantity)
                quant.reserved_quantity += max_quantity_on_quant
                reserved_quants.append((quant, max_quantity_on_quant))
                quantity -= max_quantity_on_quant
                available_quantity -= max_quantity_on_quant
            else:
                max_quantity_on_quant = min(quant.reserved_quantity, abs(quantity))
                quant.reserved_quantity -= max_quantity_on_quant
                reserved_quants.append((quant, -max_quantity_on_quant))
                quantity += max_quantity_on_quant
                available_quantity += max_quantity_on_quant

            if float_is_zero(quantity, precision_rounding=rounding) or float_is_zero(available_quantity,
                                                                                     precision_rounding=rounding):
                break
        return reserved_quants

    @api.constrains('quantity')
    def check_quantity(self):
        for quant in self:
            if float_compare(quant.quantity, 1,
                             precision_rounding=quant.product_uom_id.rounding) > 0 and quant.lot_id and quant.product_id.tracking == 'serial':
                print('hello')
                # raise ValidationError(_('A serial number should only be linked to a single product.'))


class addcheckbox(models.Model):
    _inherit = "stock.move.line"
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

    def do_un_produce(self):
        # Unlink the moves related to manufacture order
        products_finished = self.finished_move_line_ids.filtered(lambda x: (x.chick_box == True) and(x.state=='done'))

        products_raw = self.move_raw_ids.filtered(lambda x: (x.needs_lots == True) and(x.state=='done'))

        for product in products_finished:
            if product.state == 'done':
                new_serial = self.env['stock.quant'].search([('product_id','=',product.product_id.id),('lot_id', '=',product.lot_id.id)])

                for serial in new_serial:
                    if serial:

                        moves = self.env['stock.move.line'].search([('reference', '=', self.name), ('lot_id', '=', serial.lot_id.id)])
                        for move in moves:
                            serial.sudo().unlink()

                            move.unlink()
                for row in self.move_raw_ids:
                    if row.needs_lots == True and row.state=='done':
                        stock_move_id = self.env['stock.move'].search([('product_id', '=', row.product_id.id)])
                        for stock_move in stock_move_id:
                            for move_line in stock_move.active_move_line_ids:
                                if product.lot_id.id == move_line.lot_produced_id.id:
                                    new_serial2 = self.env['stock.quant'].search( [('product_id', '=', row.product_id.id),('lot_id', '=', move_line.lot_id.id)])

                                    for seria_pro in new_serial2:
                                            seria_pro.sudo().unlink()

                                            row.state='confirmed'
                    else:
                        row.state='confirmed'


                product.state='confirmed'

        moves = self.env['stock.move.line'].search([('reference', '=', self.name)])
        moves.unlink()
        self.state = 'confirmed'

    @api.multi
    def post_inventory(self):
        if self.check_box == True:

            for order in self:
                # moves_to_do = order.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel'))

                products_finished = order.finished_move_line_ids.filtered(lambda x:x.chick_box == True)
                if products_finished:
                    for item in products_finished:

                        if item.state !='done' and item.state != 'cancel':
                                new_product=self.env['stock.quant'].sudo().create({
                                            'manufacturing_id':self.id,
                                            'product_id': item.product_id.id,
                                            'product_qty': item.qty_done,
                                            'lot_id': item.lot_id.id,
                                            'location_id':12,
                                            'quantity':0,

                                        })




                                new_product.sudo().write({
                                                    'quantity' :  item.qty_done,
                                                })

                                item.state = 'done'
                                for row in order.move_raw_ids:
                                    if row.needs_lots==True:
                                                stock_move_id = self.env['stock.move'].search([('product_id', '=', row.product_id.id)])
                                                for stock_move in stock_move_id:
                                                  for move_line in stock_move.active_move_line_ids:
                                                    if row.product_id.id== stock_move.product_id.id and item.lot_id.id == move_line.lot_produced_id.id:

                                                        new_fram = self.env['stock.quant'].sudo().create({
                                                            'manufacturing_id': self.id,
                                                            'product_id': row.product_id.id,
                                                            'product_qty': 0,
                                                            'lot_id': move_line.lot_id.id,
                                                            'location_id': 12,
                                                            'quantity': 0,

                                                        })



                                                        total_first = row.product_uom_qty / order.product_qty

                                                        total = total_first * item.qty_done

                                                        new_fram.sudo().write({
                                                                    'quantity': -1*total,
                                                                })
                                                        row.state='done'
                                    else:
                                        row.state='done'
                order.state='progress'






        else:


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

                            else:
                                # Link with everything
                                moveline.write({'consume_line_ids': [(6, 0, [x for x in consume_move_lines.ids])]})


        return True
