
from odoo import api, fields, models,_

from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_round, float_compare, float_is_zero


class PRODUCTPRODUCT(models.Model):
    _inherit = 'product.product'
    forecast_count = fields.Integer(compute='_get_forecast_value', readonly=1)

    @api.multi
    @api.depends('forecast_count')
    def _get_forecast_value(self):
        for item in self:
            item.forecast_count = item.qty_available

            production_id = self.env['mrp.production'].search([('product_id', '=', item.id),('state','in',('confirmed','progress'))])
            count=0
            for rec in production_id:
                count += rec.product_qty
            item.forecast_count +=count



    @api.depends('stock_move_ids.product_qty', 'stock_move_ids.state')
    def _compute_quantities(self):
        print('hello count')
        res = self._compute_quantities_dict(self._context.get('lot_id'), self._context.get('owner_id'),
                                            self._context.get('package_id'), self._context.get('from_date'),
                                            self._context.get('to_date'))
        for product in self:
            production_id = self.env['mrp.production'].search(
                [('product_id', '=', product.id), ('state', '=', 'done')])
            count = 0
            for rec in production_id:
                count += rec.product_qty

            product.qty_available = res[product.id]['qty_available']
            product.incoming_qty = res[product.id]['incoming_qty']
            product.outgoing_qty = res[product.id]['outgoing_qty']
<<<<<<< HEAD
            product.virtual_available = product.qty_available + (product.incoming_qty - count)
=======
            product.virtual_available = product.qty_available + (product.incoming_qty - count)-product.outgoing_qty
>>>>>>> tredco_development


#region
#     def _compute_quantities_dict(self, lot_id, owner_id, package_id, from_date=False, to_date=False):
#         for stock in self.stock_quant_ids:
#             if stock.quant_check==False:
#                 domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self._get_domain_locations()
#                 domain_quant = [('product_id', 'in', self.ids)] + domain_quant_loc
#                 dates_in_the_past = False
#                 # only to_date as to_date will correspond to qty_available
#                 to_date = fields.Datetime.to_datetime(to_date)
#                 if to_date and to_date < fields.Datetime.now():
#                     dates_in_the_past = True
#
#                 domain_move_in = [('product_id', 'in', self.ids)] + domain_move_in_loc
#                 domain_move_out = [('product_id', 'in', self.ids)] + domain_move_out_loc
#                 if lot_id is not None:
#                     domain_quant += [('lot_id', '=', lot_id)]
#                 if owner_id is not None:
#                     domain_quant += [('owner_id', '=', owner_id)]
#                     domain_move_in += [('restrict_partner_id', '=', owner_id)]
#                     domain_move_out += [('restrict_partner_id', '=', owner_id)]
#                 if package_id is not None:
#                     domain_quant += [('package_id', '=', package_id)]
#                 if dates_in_the_past:
#                     domain_move_in_done = list(domain_move_in)
#                     domain_move_out_done = list(domain_move_out)
#                 if from_date:
#                     domain_move_in += [('date', '>=', from_date)]
#                     domain_move_out += [('date', '>=', from_date)]
#                 if to_date:
#                     domain_move_in += [('date', '<=', to_date)]
#                     domain_move_out += [('date', '<=', to_date)]
#
#                 Move = self.env['stock.move']
#                 Quant = self.env['stock.quant']
#                 domain_move_in_todo = [('state', 'in',
#                                         ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_in
#                 domain_move_out_todo = [('state', 'in',
#                                          ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_out
#                 moves_in_res = dict((item['product_id'][0], item['product_qty']) for item in
#                                     Move.read_group(domain_move_in_todo, ['product_id', 'product_qty'], ['product_id'],
#                                                     orderby='id'))
#                 moves_out_res = dict((item['product_id'][0], item['product_qty']) for item in
#                                      Move.read_group(domain_move_out_todo, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
#                 quants_res = dict((item['product_id'][0], item['quantity']) for item in
#                                   Quant.read_group(domain_quant, ['product_id', 'quantity'], ['product_id'], orderby='id'))
#                 if dates_in_the_past:
#                     # Calculate the moves that were done before now to calculate back in time (as most questions will be recent ones)
#                     domain_move_in_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_in_done
#                     domain_move_out_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_out_done
#                     moves_in_res_past = dict((item['product_id'][0], item['product_qty']) for item in
#                                              Move.read_group(domain_move_in_done, ['product_id', 'product_qty'], ['product_id'],
#                                                              orderby='id'))
#                     moves_out_res_past = dict((item['product_id'][0], item['product_qty']) for item in
#                                               Move.read_group(domain_move_out_done, ['product_id', 'product_qty'],
#                                                               ['product_id'], orderby='id'))
#
#                 res = dict()
#                 for product in self.with_context(prefetch_fields=False):
#                     product_id = product.id
#                     rounding = product.uom_id.rounding
#                     res[product_id] = {}
#                     if dates_in_the_past:
#                         qty_available = quants_res.get(product_id, 0.0) - moves_in_res_past.get(product_id,
#                                                                                                 0.0) + moves_out_res_past.get(
#                             product_id, 0.0)
#                     else:
#                         qty_available = quants_res.get(product_id, 0.0)
#                     res[product_id]['qty_available'] = float_round(qty_available, precision_rounding=rounding)
#                     res[product_id]['incoming_qty'] = float_round(moves_in_res.get(product_id, 0.0),
#                                                                   precision_rounding=rounding)
#                     res[product_id]['outgoing_qty'] = float_round(moves_out_res.get(product_id, 0.0),
#                                                                   precision_rounding=rounding)
#                     res[product_id]['virtual_available'] = float_round(
#                         qty_available + res[product_id]['incoming_qty'] - res[product_id]['outgoing_qty'],
#                         precision_rounding=rounding)
#
#                 return res
#             else:
#                 domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self._get_domain_locations()
#                 domain_quant = [('product_id', 'in', self.ids)] + domain_quant_loc
#                 dates_in_the_past = False
#                 # only to_date as to_date will correspond to qty_available
#                 to_date = fields.Datetime.to_datetime(to_date)
#                 if to_date and to_date < fields.Datetime.now():
#                     dates_in_the_past = True
#
#                 domain_move_in = [('product_id', 'in', self.ids)] + domain_move_in_loc
#                 domain_move_out = [('product_id', 'in', self.ids)] + domain_move_out_loc
#                 if lot_id is not None:
#                     domain_quant += [('lot_id', '=', lot_id)]
#                 if owner_id is not None:
#                     domain_quant += [('owner_id', '=', owner_id)]
#                     domain_move_in += [('restrict_partner_id', '=', owner_id)]
#                     domain_move_out += [('restrict_partner_id', '=', owner_id)]
#                 if package_id is not None:
#                     domain_quant += [('package_id', '=', package_id)]
#                 if dates_in_the_past:
#                     domain_move_in_done = list(domain_move_in)
#                     domain_move_out_done = list(domain_move_out)
#                 if from_date:
#                     domain_move_in += [('date', '>=', from_date)]
#                     domain_move_out += [('date', '>=', from_date)]
#                 if to_date:
#                     domain_move_in += [('date', '<=', to_date)]
#                     domain_move_out += [('date', '<=', to_date)]
#
#                 Move = self.env['stock.move']
#                 Quant = self.env['stock.quant']
#                 domain_move_in_todo = [('state', 'in',
#                                         ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_in
#                 domain_move_out_todo = [('state', 'in',
#                                          ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_out
#                 # moves_in_res = dict((item['product_id'][0], item['product_qty']) for item in
#                 #                     Move.read_group(domain_move_in_todo, ['product_id', 'product_qty'], ['product_id'],
#                 #                                     orderby='id'))
#                 moves_out_res = dict((item['product_id'][0], item['product_qty']) for item in
#                                      Move.read_group(domain_move_out_todo, ['product_id', 'product_qty'],
#                                                      ['product_id'], orderby='id'))
#                 quants_res = dict((item['product_id'][0], item['quantity']) for item in
#                                   Quant.read_group(domain_quant, ['product_id', 'quantity'], ['product_id'],
#                                                    orderby='id'))
#                 if dates_in_the_past:
#                     # Calculate the moves that were done before now to calculate back in time (as most questions will be recent ones)
#                     domain_move_in_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_in_done
#                     domain_move_out_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_out_done
#                     moves_in_res_past = dict((item['product_id'][0], item['product_qty']) for item in
#                                              Move.read_group(domain_move_in_done, ['product_id', 'product_qty'],
#                                                              ['product_id'],
#                                                              orderby='id'))
#                     moves_out_res_past = dict((item['product_id'][0], item['product_qty']) for item in
#                                               Move.read_group(domain_move_out_done, ['product_id', 'product_qty'],
#                                                               ['product_id'], orderby='id'))
#
#                 res = dict()
#                 for product in self.with_context(prefetch_fields=False):
#                     product_id = product.id
#                     rounding = product.uom_id.rounding
#                     res[product_id] = {}
#                     if dates_in_the_past:
#                         qty_available = quants_res.get(product_id, 0.0) -  moves_out_res_past.get(
#                             product_id, 0.0)
#                     else:
#                         qty_available = quants_res.get(product_id, 0.0)
#                     res[product_id]['qty_available'] = float_round(qty_available, precision_rounding=rounding)
#                     # res[product_id]['incoming_qty'] = float_round(moves_in_res.get(product_id, 0.0),
#                     #                                               precision_rounding=rounding)
#                     res[product_id]['outgoing_qty'] = float_round(moves_out_res.get(product_id, 0.0),
#                                                                   precision_rounding=rounding)
#                     res[product_id]['virtual_available'] = float_round(
#                         qty_available + res[product_id]['outgoing_qty'],
#                         precision_rounding=rounding)
#
#                 return res
#
#     @api.depends('stock_move_ids.product_qty', 'stock_move_ids.state')
#     def _compute_quantities(self):
#         print('hell compute')
#
#         for stock in self.stock_quant_ids:
#             if stock.quant_check==False:
#                 res = self._compute_quantities_dict(self._context.get('lot_id'), self._context.get('owner_id'),self._context.get('package_id'), self._context.get('from_date'),self._context.get('to_date'))
#                 print('quant ckeck',stock.quant_check)
#                 for product in self:
#                         product.qty_available = res[product.id]['qty_available']
#                         product.incoming_qty = res[product.id]['incoming_qty']
#                         product.outgoing_qty = res[product.id]['outgoing_qty']
#                         product.virtual_available = res[product.id]['virtual_available']
#             else:
#                 print('not update')
#                 res = self._compute_quantities_dict(self._context.get('lot_id'), self._context.get('owner_id'),
#                                                     self._context.get('package_id'), self._context.get('from_date'),
#                                                     self._context.get('to_date'))
#                 print('quant ckeck', stock.quant_check)
#                 for product in self:
#                     product.qty_available = res[product.id]['qty_available']
#
#                     product.outgoing_qty = res[product.id]['outgoing_qty']
#                     product.virtual_available = res[product.id]['virtual_available']
#



class StockQuant(models.Model):
    _inherit = 'stock.quant'
    quant_check=fields.Boolean('check Quant')

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


class Stockmoveline(models.Model):
    _inherit = "stock.move.line"

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
    def do_unreserve(self):
        for row in self.move_raw_ids:
             row.state = 'assigned'
        for production in self:
            production.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel'))._do_unreserve()
        return True

    # def do_un_produce(self):
    #     moves = self.env['stock.move.line'].search([('reference', '=', self.name)]).unlink()
    #
    #     self.state = 'confirmed'
    #     # # Unlink the moves related to manufacture order
    #     # products_finished = self.finished_move_line_ids.filtered(lambda x: (x.chick_box == True) and(x.state=='done'))
    #     #
    #     # products_raw = self.move_raw_ids.filtered(lambda x: (x.needs_lots == True) and(x.state=='done'))
    #     #
    #     # for product in products_finished:
    #     #     if product.state == 'done':
    #     #         new_serial = self.env['stock.quant'].search([('product_id','=',product.product_id.id),('lot_id', '=',product.lot_id.id)])
    #     #
    #     #         for serial in new_serial:
    #     #             if serial:
    #     #
    #     #                 moves = self.env['stock.move.line'].search([('reference', '=', self.name), ('lot_id', '=', serial.lot_id.id)])
    #     #                 for move in moves:
    #     #                     serial.sudo().unlink()
    #     #
    #     #                     move.unlink()
    #     #         for row in self.move_raw_ids:
    #     #             if row.needs_lots == True and row.state=='done':
    #     #                 stock_move_id = self.env['stock.move'].search([('product_id', '=', row.product_id.id)])
    #     #                 for stock_move in stock_move_id:
    #     #                     for move_line in stock_move.active_move_line_ids:
    #     #                         if product.lot_id.id == move_line.lot_produced_id.id:
    #     #                             new_serial2 = self.env['stock.quant'].search( [('product_id', '=', row.product_id.id),('lot_id', '=', move_line.lot_id.id)])
    #     #
    #     #                             for seria_pro in new_serial2:
    #     #                                     seria_pro.sudo().unlink()
    #     #
    #     #                                     row.state='assigned'
    #     #             else:
    #     #                 row.state='assigned'
    #     #
    #     #
    #     #         product.state='confirmed'
    #
    #     moves = self.env['stock.move.line'].search([('reference', '=', self.name)])
    #     moves.unlink()
    #     self.state = 'confirmed'

    @api.multi
    def post_inventory(self):
        if self.check_box == True:

            for order in self:
                # moves_to_do = order.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel'))

                products_finished = order.finished_move_line_ids.filtered(lambda x:x.chick_box == True)
                if products_finished:
                    for item in products_finished:

                        item.product_id.product_variant_ids.sudo().write({
                            'mrp_product_qty': item.qty_done
                        })

                        if item.state !='done' and item.state != 'cancel':
                                new_product=self.env['stock.quant'].sudo().create({
                                            'quant_check':True,
                                            'product_id': item.product_id.id,
                                            'product_qty': 0,
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

    @api.multi
    def button_mark_done(self):
        self.state='done'
        self.ensure_one()
        for wo in self.workorder_ids:
            if wo.time_ids.filtered(lambda x: (not x.date_end) and (x.loss_type in ('productive', 'performance'))):
                raise UserError(_('Work order %s is still running') % wo.name)
        self._check_lots()

