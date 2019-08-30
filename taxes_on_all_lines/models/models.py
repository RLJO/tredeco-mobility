# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ApplyAccountTaxLine(models.Model):
    _name = 'apply.account.tax.line'
    # _rec_name = tax_ids

    sale_tax_ids = fields.Many2many('account.tax', string='Taxes', required=True, domain=[('type_tax_use', '=', 'sale')])
    purchase_tax_ids = fields.Many2many('account.tax', string='Taxes',required=True, domain=[('type_tax_use', '=', 'purchase')])
    customer_invoice_tax_ids = fields.Many2many('account.tax',string="Taxes" ,required=True, domain=[('type_tax_use', '!=', 'sale')])
    vendor_bill_tax_ids = fields.Many2many('account.tax',string="Taxes" ,required=True, domain=[('type_tax_use', '!=', 'purchase')])
    
    @api.multi
    def apply_tax_on_all_lines(self):
        active_id = self.env.context.get('active_id', False)
        active_model = self.env.context.get('active_model', False)
        # import pdb; pdb.set_trace()
        if active_model == 'sale.order':
            saleorder_obj = self.env['sale.order'].browse(active_id)
            for line in saleorder_obj.order_line:
                if line.tax_id == self.sale_tax_ids:
                    pass
                else:
                    line.tax_id = self.sale_tax_ids
        elif active_model == 'purchase.order':
            purchaseorder_obj = self.env['purchase.order'].browse(active_id)
            for line in purchaseorder_obj.order_line:
                if line.taxes_id == self.purchase_tax_ids:
                    pass
                else:
                    line.taxes_id = self.purchase_tax_ids
        elif active_model == 'account.invoice':
            accountinvoice_obj = self.env['account.invoice'].browse(active_id)
            if self.customer_invoice_tax_ids:
                for line in accountinvoice_obj.invoice_line_ids:
                    if line.invoice_line_tax_ids == self.customer_invoice_tax_ids:
                        pass
                    else:
                        line.invoice_line_tax_ids = self.customer_invoice_tax_ids
            elif self.vendor_bill_tax_ids:
                for line in accountinvoice_obj.invoice_line_ids:
                    if line.invoice_line_tax_ids == self.vendor_bill_tax_ids:
                        pass
                    else:
                        line.invoice_line_tax_ids = self.vendor_bill_tax_ids

class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_apply_taxes_on_lines(self):
        tax_form_id = self.env.ref('taxes_on_all_lines.apply_taxes_all_lines_form').id
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'apply.account.tax.line',
            'views': [(tax_form_id, 'form')],
            'view_id': tax_form_id,
            'target': 'new',
            # 'context': ctx,
        }

class SaleOrderInherit(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def action_apply_taxes_on_lines(self):
        tax_form_id = self.env.ref('taxes_on_all_lines.apply_taxes_all_lines_form_purchase').id
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'apply.account.tax.line',
            'views': [(tax_form_id, 'form')],
            'view_id': tax_form_id,
            'target': 'new',
            # 'context': ctx,
        }

class SaleOrderInherit(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def action_apply_taxes_on_lines_customer_invoice(self):
        tax_form_id = self.env.ref('taxes_on_all_lines.apply_taxes_all_lines_form_customer_invoice').id
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'apply.account.tax.line',
            'views': [(tax_form_id, 'form')],
            'view_id': tax_form_id,
            'target': 'new',
            # 'context': ctx,
        }

    @api.multi
    def action_apply_taxes_on_lines_vendor_bill(self):
        tax_form_id = self.env.ref('taxes_on_all_lines.apply_taxes_all_lines_form_vendor_bill').id
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'apply.account.tax.line',
            'views': [(tax_form_id, 'form')],
            'view_id': tax_form_id,
            'target': 'new',
            # 'context': ctx,
        }