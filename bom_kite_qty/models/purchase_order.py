

from odoo import api, fields, models, _

class PurchaseOrderLiInherit(models.Model):
    _inherit = "purchase.order.line"

    def get_actual_recevied_qty(self,qty):
        for line in self:
            product_template = self.env['product.template'].search([('name','=',line.product_id.name)])
            bom_count = self.env['mrp.bom'].search_count([('product_tmpl_id', '=', product_template.id),('type','=','phantom')])
            if bom_count == 0 or bom_count >1:
                return qty
            bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', product_template.id),('type','=','phantom')])
            bom_product_count = 0
            for product_l in bom.bom_line_ids:
                bom_product_count += product_l.product_qty
            return bom.product_qty/(bom_product_count/qty)



    def _update_received_qty(self):
        for line in self:
            total = 0.0
            for move in line.move_ids:
                if move.state == 'done':
                    if move.location_dest_id.usage == "supplier":
                        if move.to_refund:
                            total -= move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom)
                    else:
                        total += move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom)
            actual_total = self.get_actual_recevied_qty(total)
            line.qty_received =actual_total