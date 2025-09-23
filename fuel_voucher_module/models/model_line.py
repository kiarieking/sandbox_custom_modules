# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class FuelVoucher(models.Model):
    '''Class to handle fuel vouchers'''

    _name = "fuel.voucher.line"
    _description = "fuel voucher lines"

    order_id =fields.Many2one('fuel.voucher', required=True, ondelete="cascade")
    product_id = fields.Many2one('product.product', string="Product", required=True, domain=[('default_code', '=', 'FUEL'), ('is_active', '=', True)])
    description = fields.Text(string="Description", required=False)
    narration = fields.Text(string="Narration")
    quantity = fields.Float("Quantity", default=0.0)
    price_unit = fields.Float("Price", default=0.0)
    amount_subtotal = fields.Float(compute="_compute_amount_subtotal")

    @api.depends('price_unit', 'quantity')
    def _compute_amount_subtotal(self):
        '''Compute amount subtotal'''

        for record in self:
            record.amount_subtotal = record.price_unit * record.quantity

    @api.onchange('product_id')
    def _autocomplete_lines(self):
        '''Autocomplete the line details based on the product'''

        for record in self:
            if record.product_id:
                record.update({"price_unit": record.product_id.list_price})
                record.update({"quantity": 1})

