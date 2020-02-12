
from odoo import api, fields, models

from odoo12.odoo.odoo.exceptions import UserError

from odoo12.odoo.odoo.models import TransientModel


class addcheckbox(models.Model):
    _inherit = "stock.move.line"

    chick_box= fields.Boolean(string="Chick Box" )

class add_checkbox(models.Model):
    _inherit = "mrp.production"

    @api.multi
    def post_inventory(self):

        for order in self:

            moves_not_to_do = order.move_raw_ids.filtered(lambda x: x.state == 'done')
            moves_to_do = order.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            for move in moves_to_do.filtered(lambda m: m.product_qty == 0.0 and m.quantity_done > 0):
                move.product_uom_qty = move.quantity_done
            moves_to_do._action_done()
            moves_to_do = order.move_raw_ids.filtered(lambda x: x.state == 'done') - moves_not_to_do
            order._cal_price(moves_to_do)
            moves_to_finish = order.move_finished_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            moves_to_finish._action_done()
            order.action_assign()
            consume_move_lines = moves_to_do.mapped('active_move_line_ids')
            for moveline in moves_to_finish.mapped('active_move_line_ids'):
                if moveline.chick_box:
                    if moveline.product_id == order.product_id and moveline.move_id.has_tracking != 'none':
                        if any([not ml.lot_produced_id for ml in consume_move_lines]):
                            raise UserError(_('You can not consume without telling for which lot you consumed it'))
                        # Link all movelines in the consumed with same lot_produced_id false or the correct lot_produced_id
                        filtered_lines = consume_move_lines.filtered(lambda x: x.lot_produced_id == moveline.lot_id)
                        moveline.write({'consume_line_ids': [(6, 0, [x for x in filtered_lines.ids])]})
                    else:
                        # Link with everything
                        moveline.write({'consume_line_ids': [(6, 0, [x for x in consume_move_lines.ids])]})

        return True
