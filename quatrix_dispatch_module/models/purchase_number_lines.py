# -*- coding: utf-8 -*-
'''Purchase Lines Model'''
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PurchaseLines(models.Model):
    '''Purchase Lines Class'''
    _name = 'purchase.number.line'
    _description = 'purchase.number.line'
    _order = 'purchase_id'

    purchase_id =fields.Many2one('purchase.number', required=True, ondelete="cascade")
    product_id = fields.Many2one('product.product', string="Product", ondelete="restrict",required=True, domain=[('is_active', '=', True)])
    optional_product_id = fields.Many2one('product.product', string="Optional Product", ondelete="restrict",required=False, domain=[('is_active', '=', True)])
    quantity = fields.Float(string="Quantity")
    remaining_quantity = fields.Float(string="Remaining Trips", compute="_compute_remaining_trips")
    trips_completed = fields.Float(string="Completed", compute="_compute_trips_completed", default=0)
    name = fields.Char(string="Description")
    line = fields.Text(string="Line")
    price_unit = fields.Float(string="Unit Price", compute="_autofill_prices")
    amount_subtotal = fields.Float(compute="_compute_subtotal", string="Subtotal")

    # _sql_constraints = [('order_no_unique', 'unique(order_no)', 'The delivery number entered has already been used. You cannot have more than one dispatch order with the same delivery(order) number.')]

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        '''Compute totals for dispatch lines'''
        for record in self:
            record.amount_subtotal = (float(record.price_unit) * record.quantity)

    @api.depends('quantity', 'trips_completed')
    def _compute_remaining_trips(self):
        for record in self:
            if isinstance(record.id, int):
                self._compute_trips_completed()
                record.remaining_quantity = int(record.quantity) - int(record.trips_completed)

            return record.remaining_quantity or 0

    @api.depends('product_id')
    def _autofill_prices(self):
        '''Autofill list prices from product selected'''
        for record in self:
            record.update({"price_unit": float(record.product_id.list_price)})

    @api.model
    def _compute_trips_completed(self):
        for record in self:
            completed = []

            if isinstance(record.id, int):
                dispatched_lpos = self.env['purchase.dispatch.line'].search([
                    ('order_id.purchase_id.id', '=', record.purchase_id.id),
                    ('order_id.status', '!=', 'cancel')])

                if dispatched_lpos:
                    for dispatch_lpo in dispatched_lpos:
                        for line in dispatch_lpo:
                            if line.product_id == record.product_id:
                                completed.append(float(line.quantity))
                                
                record.write({'trips_completed': sum(completed)})
            else:
                record.write({'trips_completed': int(0)})
