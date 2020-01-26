# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round

class StockPickingCT(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def button_validate(self):
        self.ensure_one()
        if self.picking_type_code in ['outgoing','internal']:
            for move_id in self.move_ids_without_package:
                if move_id.quantity_done > move_id.reserved_availability:
                    raise ValidationError(_('You are allowed to continue because there is not enough quantity in stock'))
        return super(StockPickingCT, self).button_validate()


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    @api.model
    def default_get(self, fields):
        if len(self.env.context.get('active_ids', list())) > 1:
            raise UserError(_("You may only return one picking at a time."))
        res = super(ReturnPicking, self).default_get(fields)

        move_dest_exists = False
        product_return_moves = []
        picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        if picking:
            print("wewewewegg")
            # ----------------------------------------
            # of followers and "3" is the partner ID
            # thread_pool = self.pool.get('mail.thread')
            # thread_pool.message_post(
            #     body="order has been returned",
            #     partner_ids=[picking.sale_id.warehouse_id.partner_id.id],
            #     subtype='mail.mt_comment',
            #     notif_layout='mail.mail_notification_light',
            # )
            print(picking.sale_id.warehouse_id.partner_id.id)
            print('sssss')
            print(picking.partner_id.id)
            self.env['mail.message'].sudo().create({'message_type': "notification",
                                             "subtype": self.env.ref("mail.mt_comment").id,
                                             'body': _("order has been returned"),
                                             'subject': _("order has been returned"),
                                             'needaction_partner_ids': [picking.partner_id.id],
                                             'model': self._name,
                                             'res_id': self.id,
                                             })
            # ----------------------------------------
            res.update({'picking_id': picking.id})
            if picking.state != 'done':
                raise UserError(_("You may only return Done pickings."))
            for move in picking.move_lines:
                if move.scrapped:
                    continue
                if move.move_dest_ids:
                    move_dest_exists = True
                quantity = move.product_qty - sum(
                    move.move_dest_ids.filtered(lambda m: m.state in ['partially_available', 'assigned', 'done']). \
                    mapped('move_line_ids').mapped('product_qty'))
                quantity = float_round(quantity, precision_rounding=move.product_uom.rounding)
                product_return_moves.append((0, 0, {'product_id': move.product_id.id, 'quantity': quantity,
                                                    'move_id': move.id, 'uom_id': move.product_id.uom_id.id}))

            if not product_return_moves:
                raise UserError(
                    _("No products to return (only lines in Done state and not fully returned yet can be returned)."))
            if 'product_return_moves' in fields:
                res.update({'product_return_moves': product_return_moves})
            if 'move_dest_exists' in fields:
                res.update({'move_dest_exists': move_dest_exists})
            if 'parent_location_id' in fields and picking.location_id.usage == 'internal':
                res.update({
                               'parent_location_id': picking.picking_type_id.warehouse_id and picking.picking_type_id.warehouse_id.view_location_id.id or picking.location_id.location_id.id})
            if 'original_location_id' in fields:
                res.update({'original_location_id': picking.location_id.id})
            if 'location_id' in fields:
                location_id = picking.location_id.id
                if picking.picking_type_id.return_picking_type_id.default_location_dest_id.return_location:
                    location_id = picking.picking_type_id.return_picking_type_id.default_location_dest_id.id
                res['location_id'] = location_id
        return res