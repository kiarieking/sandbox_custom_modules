'''Purchase Dispatch Lines Model'''
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PurchaseLines(models.Model):
    '''Purchase Lines Class'''
    _name = 'purchase.dispatch.line'
    _description = 'purchase.dispatch.line'
    _order = 'order_id'

    order_id =fields.Many2one('purchase.dispatch', required=True, ondelete="cascade")
    product_id = fields.Many2one('product.product',
        string="Product", ondelete="restrict",required=True, domain=[('is_active', '=', True)])
    order_no = fields.Char(string="Delivery No",required=True)
    quantity = fields.Float(string="Qty")
    description = fields.Text(string="Description",readonly=False, required=True, help="Enter the Destination/Distributor", default=" ")
    notes = fields.Text(string="Line")
    price_unit = fields.Float(string="Unit Price", default=0.0)
    carrier_price = fields.Float(string="Carrier Charges", readonly=False, default=False, compute="update_carrier_charges_if_val_is_zero", store=True)
    additional_charges = fields.Float(string="Additional Charges", default=0.0)
    amount = fields.Float(compute="_compute_subtotal", string="Subtotal")
    purchase_id = fields.Many2one(related='order_id.purchase_id')

    _sql_constraints = [('order_no_unique', 'unique(order_no)', 'The delivery number entered already exists.')]

    @api.depends('quantity', 'price_unit', 'additional_charges')
    def _compute_subtotal(self):
        '''Compute totals for dispatch lines'''
        for record in self:
            record.amount = (
                float(record.price_unit) * record.quantity) + float(record.additional_charges)
 
    def check_quantities(self):
        '''Check orders have not been exceeded before write'''
        for record in self:
            domain = [
                ('product_id', '=', record.product_id.id),
                ('purchase_id', '=', record.purchase_id.id)]

            line_details = self.env['purchase.number.line'].search_read(domain)

            lpo_domain = [
                ('order_id.purchase_id', '=', record.purchase_id.id),
                ('product_id','=',record.product_id.id)
            ]

            lpo_lines = self.env['purchase.dispatch.line'].search(lpo_domain)

            if lpo_lines is not None:
                quantity_list = []

                for line in lpo_lines:
                    quantity_list.append(line.quantity)

                for this in line_details:
                    if this["quantity"] - (sum(quantity_list)) < 0:
                        raise UserError(_('Quantities/Trips for %s under the selected LPO have been exhausted.'%(record.product_id.name)))

    @api.onchange('product_id')
    def _autofill_lines(self):
        '''Compute line details based on product order created'''
        for record in self:

            if record.purchase_id:
                domain = [
                    ('product_id', '=', record.product_id.id),
                    ('purchase_id', '=', record.purchase_id.id)]

                line_details = self.env['purchase.number.line'].search_read(domain)

                if record.product_id.id and len(line_details) == 0:
                    raise UserError(_('No such route in the chosen PO Number'))

                for line_detail in line_details:
                    try:
                        if record.quantity == 0:
                            record.update({'quantity': 1})
                        record.update({'notes': line_detail['line']})
                        record.update({'price_unit': float(line_detail['price_unit'])})

                    except Exception as exception:
                        raise UserError(_(str(exception)))

            else:
                try:
                    if record.quantity == 0:
                        record.update({'quantity': 1})
                    record.update({'notes': ''})
                    record.update({'price_unit': float(record.product_id.list_price)})

                except Exception as exception:
                    raise UserError(_(exception))

    @api.onchange('purchase_id')
    def autocomplete_lines_on_purchase_id(self):
        '''Allow dispatch lines to update on purchase id update'''

        if self.purchase_id:
            for record in self:
                if record.product_id:
                    self._autofill_lines()

    @api.onchange('product_id', 'quantity')
    def update_carrier_charges(self):
        for record in self:
            record.update({'carrier_price': float(record.product_id.standard_price) * record.quantity})
    
    @api.depends('product_id', 'quantity')
    def update_carrier_charges_if_val_is_zero(self):
        for record in self:
            if not record.carrier_price or int(record.carrier_price) == 0:
                record.update({'carrier_price': float(record.product_id.standard_price) * record.quantity})


