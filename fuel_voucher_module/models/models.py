# -*- coding: utf-8 -*-
import phonenumbers, re
import json
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class FuelVoucher(models.Model):
    '''handle fuel vouchers'''

    _name = "fuel.voucher"
    _description = "fuel voucher"
    _order = "name desc"

    date = fields.Datetime(string="Filling Date", default=lambda self: fields.datetime.now(), required=True)
    name = fields.Char(string='Quotation Number', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    vehicle_id = fields.Many2one('fleet.vehicle',string="Vehicle", required=True)
    carrier_id = fields.Many2one('res.partner', string="Carrier/Subcontractor", compute="_get_carrier", readonly=False, store=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    status = fields.Selection(
        [('draft', "Quotation"),('order', "Fuel Order"),
        ('posted', "Posted") , ('cancel', "Cancelled")], default='draft')
    reference_number = fields.Char("Reference", required=False)
    invoice_number = fields.Char('Invoice Number', store=True)
    fuel_log_id = fields.Char("Fuel Log ID", store=True)
    lpo_voucher_number = fields.Char("LPO Voucher Number", required=False)
    driver_phone_number = fields.Char("Driver Phone number", required=True)
    amount_total = fields.Monetary(string="Amount Total", compute="_compute_amount_total")
    currency_id = fields.Many2one('res.currency', 'Currency', compute='_compute_currency_id')
    order_ids = fields.One2many('fuel.voucher.line', 'order_id')

    _sql_constraints = [('lpo_voucher_number_unique', 'unique(lpo_voucher_number)', 'The LPO Voucher number entered already exists.')]

    @api.model
    def create(self, vals):
        '''Create a fuel voucher and create a new sequence number'''

        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('fuel.order') or _('New')
        result =super(FuelVoucher, self).create(vals)
        result.validate_mobile()
        result.match_fuel_to_dispatch_records()
        return result

    def write(self, vals):
        '''Edit an existing fuel voucher'''

        res =super(FuelVoucher, self).write(vals)
        self.match_fuel_to_dispatch_records()
        return res
    
    @api.depends('order_ids.amount_subtotal')
    def _compute_amount_total(self):
        '''Calculate total amount from lines'''

        for record in self:
            amount_total = 0.0
            for line in record.order_ids:
                amount_total += line.amount_subtotal
            record.update({'amount_total': amount_total })

    @api.depends()
    def _compute_currency_id(self):
        '''Return active company currency, expected KSH'''

        for record in self:
            record.currency_id = self.env.user.company_id.sudo().currency_id.id

    @api.depends('vehicle_id')
    def _get_carrier(self):
        '''select carrier automatically when selecting a vehicle'''

        for record in self:
            record.update({'carrier_id': record.vehicle_id.carrier_id})
    
    @api.depends('driver_phone_number')
    def validate_mobile(self):
        """ Raise a ValidationError if the number entered is not a valid kenyan mobile number."""

        # for record in self:
        #     if record.driver_phone_number:
        #         if len(record.driver_phone_number) != 13:
        #             raise UserError(_("Invalid mobile number! Please use format +254712345678"))

        #         phone = phonenumbers.parse(record.driver_phone_number, "KE")
        #         if phonenumbers.is_valid_number(phone):
        #             print(phone)
        #         else:
        #             raise UserError(_("Invalid mobile number! Please use format +254712345678"))
        self.ensure_one()
        
        pattern = r"^(?:\+?254|0)(?: |)\d{3}(?: |)\d{3}(?: |)\d{3}$"
        match = re.fullmatch(pattern, self.driver_phone_number)
        if not match:
            raise UserError(_(f"{self.driver_phone_number} is invalid! Kindly check mobile number."))
        
        return True

    def action_confirm(self):
        '''Button function to update fuel order status to confirmed'''

        for record in self:
            self.match_fuel_to_dispatch_records()
            record.update({"status": "order"})

    def action_reset(self):
        '''Reset cancelled orders'''
        for record in self:
            record.update({"status": 'draft'})

    def action_cancel(self):
        '''Cancel an order that has not been posted'''
        for record in self:
            record.update({"status": "cancel"})

    def action_post(self):
        '''Create a draft invoice and create fuel logs'''

        self.match_fuel_to_dispatch_records()
        self._action_post_invoice_lines()
        self.update({'status': 'posted'})
        self.post_fuel_log_against_vehicle_driver()
    
    def _get_invoice_document_ids(self):
        '''Get invoice id of related fuel order, Create a new invoice for fuel order if an invoice for this order does not exist'''

        invoice_ids = []

        invoice_order_ids = self.env['account.move'].search([
            ('partner_id', '=', self.carrier_id.id),
            ('state', '=', 'draft'), ('move_type', '=', 'out_invoice')])
        journals = self.env['account.journal'].search_read([('type','=','sale')])
        journal_id = journals[0]['id']

        if not invoice_order_ids:
            for record in self:
                vals = {
                        'invoice_origin': record.name,
                        'ref': record.name,
                        'partner_id': record.carrier_id.id,
                        'invoice_date': record.date,
                        "currency_id": record.currency_id.id,
                        'move_type':'out_invoice',
                        'journal_id': journal_id
                    }

                invoice_id = self.env['account.move'].sudo().create(vals)

                if invoice_id.name:
                    self.update({"invoice_number": invoice_id.name})

                return invoice_id.id
        else:
            for invoice_order_id in invoice_order_ids:
                invoice_ids.append(invoice_order_id)
            if len(invoice_ids) > 1:
                raise UserError(_('You have more than one open invoice quotations for {}.'.format(self.carrier_id.name)))
            else:
                invoice_id = invoice_order_ids
                if invoice_id.name:
                    self.update({"invoice_number": invoice_id.name})

                return invoice_id.id

    def _action_post_invoice_lines(self):
        '''Post order lines to invoice lines'''

        order_nos = []
        lines = []

        invoice_id = self._get_invoice_document_ids()
        _logger.info(f'Invoice ids: {invoice_id}')

        if not invoice_id:
            raise UserError(_('An error occured, could not obtain a invoice id'))
        
        move_id = self.env['account.move'].search([('id', '=', invoice_id),
            ('move_type', '=', 'out_invoice'), ('state', '=', 'draft')])

        for record in self:
            invoice_order_line_ids = self.env['account.move.line'].search([('move_id', '=', invoice_id)])
            
            _logger.info(f'invoice_order_line_ids: {invoice_order_line_ids}')

            if invoice_order_line_ids:
                for invoice_order_line_id in invoice_order_line_ids:
                    order_nos.append(invoice_order_line_id.order_no)

            for order_id in record.order_ids:
                line_vals = [(0, 0, {
                    "product_id": order_id.product_id.id,
                    "name": order_id.description,
                    "quantity": order_id.quantity,
                    "order_no": record.name,
                    "dates": self.date,
                    "price_unit": order_id.price_unit,
                    "move_id": invoice_id,
                })]

                if record.reference_number not in order_nos:
                    lines.append(line_vals)

        for line in lines:
            # Update all lines
            _logger.info(f'Move ids: {move_id}')
            move_id.update({'invoice_line_ids': line})
                

        try:
            # Post created fuel order invoice
            move_id.action_post()
            self.update({"invoice_number": move_id.name})
            if move_id.name:
                self.update({"invoice_number": move_id.name})

        except Exception as error:
            raise UserError(str(error))
    
    def match_fuel_to_dispatch_records(self):
        '''Additional methods to process fuel matching to dispatch records'''

        if self.reference_number:
            return

        linked = []
        dispatches = []

        filling_date = self.date.strftime("%Y-%m-%d")
        filling_date_forward = self.date + timedelta(days=1)

        vouchers = self.env['fuel.voucher'].search([('date', '>=', filling_date), ('date', '<=', filling_date_forward), ('vehicle_id','=',self.vehicle_id.id)])
        for voucher in vouchers:
            if voucher.reference_number:
                linked.append(voucher.reference_number)

        dispatch_records = self.env['quatrix.dispatch'].search([('fuel_voucher_count','=',0), ('date_dispatch', '>=', filling_date), ('date_dispatch', '<=', filling_date_forward), ('vehicle_id','=',self.vehicle_id.id)])
        eabl_dispatch_records = self.env['purchase.dispatch'].search([('fuel_voucher_count','=',0), ('date_dispatch', '>=', filling_date), ('date_dispatch', '<=', filling_date_forward),('vehicle_id','=',self.vehicle_id.id)])
        
        for dispatch in dispatch_records:
            if dispatch.name not in linked:
                dispatches.append(dispatch)
  
        for dispatch in eabl_dispatch_records:
            if dispatch.fuel_voucher_count == 0:
                dispatches.append(dispatch)

        for dispatch in dispatches:
            dispatch_name = dispatch.name
            return self.update({'reference_number': dispatch_name})
    
    def post_fuel_log_against_vehicle_driver(self):
        '''Create a fuel log for the vehicle after a voucher has been created.'''

        fuel_logger = self.env['fleet.vehicle.log.services']
        fuel_service = self.env['fleet.service.type'].search([('name', '=', 'Refueling')])

        vals = {}

        for record in self:
            vals['date'] = record.date
            vals['vehicle_id'] = record.vehicle_id.id
            vals['purchaser_id'] = record.vehicle_id.driver_id.id
            vals['vendor_id'] = record.company_id.id

            litre = 0
            price_per_litre = 0

            for line in record.order_ids:
                litre += line.quantity
                price_per_litre = line.price_unit

            vals['liter'] = litre
            vals['price_per_liter'] = price_per_litre
            vals['amount'] = record.amount_total
            vals['inv_ref'] = record.invoice_number
            vals['notes'] = f"Fuel for dispatch order number: {record.reference_number}\nFuel Voucher Number: {record.name}"
            vals['service_type_id'] = fuel_service.id

        try:
            fuel_log_id = fuel_logger.sudo().create(vals)
            if fuel_logger.id:
                self.update({'fuel_log_id': fuel_log_id.id})
        except Exception as e:
            raise UserError(str(e))
    
    @api.depends('status')
    @api.onchange('status')
    def find_fuel_invoices(self):
        '''Find all fuel invoices for posted entries and update invoice numbers'''

        for record in self:

            if self.status != 'posted':
                return
            
            account_move_id = self.env['account.move'].search([('ref', '=', self.name), ('state', '!=', 'cancel'), ('state','=','posted')])
            if account_move_id:
                for move_id in account_move_id:
                    record.update({'invoice_number': move_id.name})






