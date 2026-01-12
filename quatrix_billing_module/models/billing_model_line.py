'''Dispatch Lines Model'''
from odoo import models, fields, api
from odoo.exceptions import UserError

class BillingLines(models.Model):
    '''Billing Lines Class'''
    _name = 'billing.order.line'
    _description = 'billing.order.line'
    _order = 'order_id'

    order_id =fields.Many2one('billing.order', required=True, ondelete="cascade")
    quantity = fields.Float(string="Qty")
    product_id = fields.Many2one('product.product', string="Product", ondelete="restrict", required=True)
    name = fields.Char(string="Description")
    notes = fields.Text(string="Notes")
    price_unit = fields.Float(string="Unit Price")
    amount_subtotal = fields.Float(compute="_value_pc", string="Subtotal")
    important_field_do_not_delete = fields.Text(compute="_autofill_lines")

    @api.onchange('product_id')
    def onchange_billing_type(self):
        '''Get products based on default code'''
        for record in self:
            res = {}
            res['domain'] = {'product_id': [('is_active', '=', True), ('partner_id', '=', False)]}
            return res

    @api.depends('quantity', 'price_unit')
    def _value_pc(self):
        '''Compute totals for dispatch lines'''
        for record in self:
            record.amount_subtotal = float(record.price_unit) * record.quantity
    
    @api.depends('product_id')
    @api.onchange('product_id')
    def _autofill_lines(self):
        '''Autofill lines on product select'''
        for record in self:
            record.update({
                "important_field_do_not_delete": 1,
                "quantity": 1,
                "price_unit": float(record.product_id.list_price)
                })
            