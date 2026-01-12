
from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError

class CarrierOrders(models.Model):
    _name = 'carrier.order'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Carrier Orders'
    _order='date desc'

    name = fields.Char(string='Quotation Number', required=True,
        copy=False, readonly=True, index=True, default=lambda self: _('New'))
    product_id = fields.Many2one('product.product',
        string="Product", ondelete="restrict", required=True,)
    date = fields.Datetime("Date", default=datetime.now(), required=True)
    order_no = fields.Char("Delivery No.", required=True)
    reference = fields.Char("Reference No.", required=True)
    description = fields.Text(string="Description", readonly=False, required=True)
    vehicle_id = fields.Many2one('fleet.vehicle',
        string="Vehicle Registration", ondelete="restrict",required=True)
    vendor_id = fields.Many2one('res.partner', string="Carrier/Subcon",
        required=True, change_default=True, index=True, tracking=1, readonly=False, compute="_get_vendor", store=True)
    user_id = fields.Many2one('res.users', compute="_get_current_user", string='Staff',
        ondelete="restrict", default=lambda self: self.env.user)
    carrier_price = fields.Float(string="Cost", required=True)
    quantity = fields.Float(string="Quantity", required=True)
    amount = fields.Float(compute="_compute_subtotal", string="Amount")
    currency_id = fields.Many2one('res.currency', 'Currency', compute='_compute_currency_id')
    status = fields.Selection(
        [('draft', "Quotation"),('order', "Order"),
        ('posted', "Posted") , ('cancel', "Cancelled")], default='draft')
    
    _sql_constraints = [('order_no_unique', 'unique(order_no)', 'The delivery number entered already exists.')]

    @api.model
    def create(self, vals):
        '''Create a record and create a new sequence number'''
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('carrier.order') or _('New')
        result =super(CarrierOrders, self).create(vals)
        return result
    
    @api.depends('vehicle_id')
    def _get_vendor(self):
        '''select vendor automatically when selecting a vehicle'''
        for record in self:
            record.update({'vendor_id': record.vehicle_id.carrier_id})
    
    @api.depends()
    def _get_current_user(self):
        '''Return active user'''
        self.update({'user_id' : self.env.user.id})
    
    @api.depends()
    def _compute_currency_id(self):
        '''Return active company currency, expected KSH'''
        for record in self:
            record.currency_id = self.env.user.company_id.sudo().currency_id.id
    
    @api.depends('quantity', 'carrier_price')
    def _compute_subtotal(self):
        '''Compute totals'''
        for record in self:
            record.amount = float(record.carrier_price) * record.quantity

    def action_post(self):
        for record in self:
            try:
                self._action_post_purchase_lines()
                record.update({ 'status': 'posted'})
            except Exception as e:
                raise UserError(e)

    def action_confirm(self):
        for record in self:
            record.update({ 'status': 'order'})

    def action_reset(self):
        for record in self:
            record.update({ 'status': 'draft'})
    
    def action_cancel(self):
        for record in self:
            purchase_record = self.env['purchase.order'].search([
                    ('order_line.order_no', '=', record.order_no),
                    ('state', '=', 'draft')])
            for order_line in purchase_record.order_line:
                if order_line.order_no == record.order_no:
                    self.env['purchase.order.line'].search([('id', '=', order_line.id)]).unlink() or purchase_record.unlink(order_line.id)
                    self.update({'status': 'cancel'})
            record.update({ 'status': 'cancel'})

    def _get_purchase_document_id(self):
        '''Get purchase id or create a purchase_id'''

        purchase_ids = []

        purchase_order_ids = self.env['purchase.order'].search([
            ('partner_id', '=', self.vendor_id.id),
            ('state', '=', 'draft')])
           
        if not purchase_order_ids:
            for record in self:
                vals = {
                        'origin': record.name,
                        'partner_id': record.vendor_id.id,
                        "user_id": record.user_id.id,
                        "currency_id": record.currency_id.id,
                        "date_order": record.date,
                    }

                purchase_id = self.env['purchase.order'].sudo().create(vals)

                return purchase_id.id
        else:
            for purchase_order_id in purchase_order_ids:
                purchase_ids.append(purchase_order_id)
            if len(purchase_ids) > 1:
                raise UserError(_('You have more than one open purchase quotations for {}.'.format(self.vendor_id.name)))
            else:
                purchase_id = purchase_order_ids.id
                return purchase_id
    
    def _action_post_purchase_lines(self):
        '''Post order lines to quotation lines'''
        order_nos = []

        purchase_id = self._get_purchase_document_id()

        taxes_id = None #If vendor is not vatable don't apply any taxes.


        if not purchase_id:
            raise UserError(_('An error occured, could not obtain a purchase id'))

        purchase_order_line_ids = self.env['purchase.order.line'].search([('order_id', '=', purchase_id)])
        purchase_order_ids = self.env['purchase.order'].search([('id', '=', purchase_id)])
        for purchase_order_line_id in purchase_order_line_ids:
            order_nos.append(purchase_order_line_id.order_no)

        for record in self:
            if record.vendor_id.id == purchase_order_ids.partner_id.id:
                if record.vendor_id.is_partner_vatable:
                    taxes_id = record.product_id.taxes_id

                line_vals = [(0, 0, {
                    "date":record.date,
                    "order_no": record.order_no,
                    "product_id": record.product_id.id,
                    'product_uom' : record.product_id.uom_id.id,
                    "name": (record.vehicle_id.license_plate + ":" + record.description) or record.vehicle_id.license_plate,
                    "product_qty": record.quantity,
                    "price_unit": record.carrier_price,
                    "order_id": purchase_id,
                    "taxes_id": taxes_id,
                    "date_planned": record.date
                })]

                try:
                    purchase_order_ids.write({ 'order_line': line_vals })
                    self.update({'status' : 'order'})
                except Exception as error:
                    raise UserError(error)
