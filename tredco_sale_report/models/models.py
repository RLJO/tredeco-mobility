# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = "sale.order"

    standard_price = fields.Float(
        'Product Cost Price', digits=dp.get_precision('Product Price'), compute='_compute_product_cost', store=True)

    @api.depends('order_line.product_id.standard_price', 'order_line.product_uom_qty')
    def _compute_product_cost(self):
        for order in self:
            sum_cost_price = 0.0
            for line in order.order_line:
                sum_cost_price += line.product_id.standard_price * line.product_uom_qty
            order.standard_price = sum_cost_price

class SaleReport(models.Model):
    _inherit = 'sale.report'

    standard_price = fields.Float(
        'Product Cost Price', digits=dp.get_precision('Product Price'))


    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['standard_price'] = ", s.standard_price as standard_price"
        # groupby += ', s.standard_price'
        res = super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
        return res
