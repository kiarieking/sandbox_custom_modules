'''Dispatch Lines Model'''
import re
import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class DispatchLines(models.Model):
    '''Dispatch Lines Class'''

    _name = 'quatrix.dispatch.line'
    _description = 'quatrix.dispatch.line'
    _order = 'order_id'

    order_id =fields.Many2one('quatrix.dispatch', required=True, ondelete="cascade")
    product_id = fields.Many2one('product.product',
        string="Product", ondelete="restrict", required=True, domain=[('is_active', '=', True)])
    order_no = fields.Char(string="Delivery No",required=True)
    quantity = fields.Float(string="Qty")
    description = fields.Text(string="Description", readonly=False, required=True, help="Enter the destination", default=" ")
    notes = fields.Text(string="Narration", help="Enter the cargo description")
    price_unit = fields.Float(string="Unit Price", default=0.0)
    carrier_price = fields.Float(string="Carrier Charges", default=False, compute="_update_carrier_charges_if_val_is_zero", store=True, readonly=False)
    additional_charges = fields.Float(string="Additional Charges", default=0.0)
    amount = fields.Float(compute="_compute_subtotal", string="Subtotal")

    _sql_constraints = [('order_no_unique', 'unique(order_no)', 'The delivery number entered already exists.')]
    
    def _check_order_no_duplicate(self, order_no):
        _logger.info(f"Check if {order_no} exists.")
        
        self.env.cr.execute("""
            SELECT qdl.order_no, qd.name FROM quatrix_dispatch_line qdl 
            JOIN quatrix_dispatch qd ON qd.id = qdl.order_id 
            WHERE qdl.order_no like '%%' || %s || '%%'
        """, (order_no, ))
        order_line = self.env.cr.fetchall()
        _logger.info(f"Found record(s) {order_line} for delivery no.: {order_no}.")
        
        if order_line:
            raise ValidationError(f"Delivery number exists! Check record {order_line[0][1]}:{order_line[0][0]}")

    @api.depends('quantity', 'price_unit', 'additional_charges')
    def _compute_subtotal(self):
        '''Compute totals for dispatch lines'''

        for record in self:
            record.amount = (float(record.price_unit) * record.quantity) + float(record.additional_charges)

    @api.onchange('product_id', 'quantity')
    def _autofill_lines(self):
        ''' Autofill dispatch order line based on changes on product id'''

        for record in self:
            if record.order_id.partner_id.property_product_pricelist and \
                record.order_id.partner_id.property_product_pricelist.name == 'USD Customer':
                usd = record.env['res.currency'].search([('name', '=', 'USD')])
                kes = record.env['res.currency'].search([('name', '=', 'KES')])
                record.update({'price_unit': kes.compute(record.product_id.list_price, usd)})
            else:
                record.update({'price_unit': float(record.product_id.list_price)})

            if record.quantity == 0:
                record.update({'quantity': 1 })
    
    @api.depends('product_id', 'quantity', 'carrier_price')
    def _update_carrier_charges_if_val_is_zero(self):
        
        for record in self:
            if not record.carrier_price or int(record.carrier_price == 0):
                record.carrier_price = float(record.product_id.standard_price) * record.quantity
                record.update({'carrier_price': float(record.product_id.standard_price) * record.quantity})
    
    @api.onchange('product_id', 'quantity')
    def update_carrier_charges(self):

        for record in self:
            record.update({'carrier_price': float(record.product_id.standard_price) * record.quantity})
    
    @api.model
    def create(self, vals):
        if 'order_no' in vals:
            self._check_order_no_duplicate(vals['order_no'])
        return super().create(vals)
        
    def write(self, vals):
        if 'order_no' in vals:
            self._check_order_no_duplicate(vals['order_no'])
        return super().write(vals)    
    
