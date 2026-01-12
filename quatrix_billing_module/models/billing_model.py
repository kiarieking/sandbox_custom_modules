# -*- coding: utf-8 -*-
'''Manage customer/supplier invoice relationship in regards to supplier billing'''
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class Billing(models.Model):
    '''Billing class'''
    _name = 'billing.order'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'billing.order'
    _order = 'date_billing desc'

    partner_id = fields.Many2one('res.partner', string="Carrier", required=True, change_default=True, index=True, tracking=1,)
    client_id = fields.Many2one('res.partner', string="Customer", required=False, change_default=True, index=True, tracking=1,)
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    reference_number = fields.Char(string='Reference', readonly=False)
    date_billing = fields.Date(string='Billing Date', default=lambda self: fields.datetime.now(), required=True)
    name = fields.Char(string='Quotation Number', required=True,
        copy=False, readonly=True, index=True, default=lambda self: ('New'))
    amount_total = fields.Float(string='Amount Total', compute='_compute_total_amount')
    currency_id = fields.Many2one('res.currency', 'Currency', compute='_compute_currency_id')
    user_id = fields.Many2one('res.users', compute="_get_current_user", string='Staff',
        ondelete="restrict", default=lambda self: self.env.user)
    order_line = fields.One2many('billing.order.line', 'order_id')
    partner_invoice_id = fields.Many2one(
        'res.partner', string='Invoice Address',
        readonly=True,
        states={'draft': [('readonly', False)],
             'posted': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)
    partner_shipping_id = fields.Many2one(
        'res.partner', string='Delivery Address', readonly=True,
        states={'draft': [('readonly', False)],
             'posted': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)
    company_id = fields.Many2one('res.company', 'Company',
        required=True, index=True, default=lambda self: self.env.company)
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms', readonly=True, states={'draft': [('readonly', False)]})
    status = fields.Selection(
        [('draft', "Quotation"),
        ('order', "Confirmed"),
        ('posted', "Invoiced"),
        ('cancel', "Cancelled")]
        , default='draft')
    billing_client_state = fields.Selection(
        [('paid', 'Paid'),('pending', "Pending")], default="pending")

    @api.depends()
    def _get_current_user(self):
        '''Return active user'''
        self.update({'user_id' : self.env.user.id})

    @api.model
    def create(self, vals):
        '''Create a dispatch and create a new sequence number'''
        if vals.get('name', ('New')) == ('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('billing.order') or ('New')
        result =super(Billing, self).create(vals)
        self._check_customer_based_on_product()
        return result

    @api.depends('order_line.amount_subtotal')
    def _compute_total_amount(self):
        '''Calculate total mount from lines'''
        for record in self:
            amount_total = 0.0
            for line in record.order_line:
                amount_total += line.amount_subtotal
            record.update({'amount_total': amount_total })

    @api.depends()
    def _compute_currency_id(self):
        '''Return active company currency, expected KSH'''
        for record in self:
            record.currency_id = self.env.user.company_id.sudo().currency_id.id

    def action_confirm(self):
        '''Create invoice quotation'''
        self._check_customer_based_on_product()
        return self.update({'status': 'order'})

    def action_post(self):
        '''Create invoice quotation'''
        self._check_customer_based_on_product()
        self._action_post_invoice_lines()
        return self.update({'status': 'posted'}) 

    def action_reset(self):
        '''Reset an order to quotations'''
        self.update({'status' : 'draft'})

    def action_cancel(self):
        '''Cancel a billing order and remove lines from draft invoice'''
        self.update({'status' : 'cancel'})
        # return self._action_remove_lines_from_draft_invoice()
    def _check_customer_based_on_product(self):
        for record in self:
            for line in record.order_line:
                product_id = line.product_id

                if product_id.is_inventory:
                    pass
                else:
                    if not record.client_id:
                        raise UserError("Customer/Shipper is required.")

    def _get_invoice_document_ids(self):
        '''Get sale id or create a sale_id'''
        invoice_ids = []

        journal_id = None

        # journal_ids = self.env['account.journal'].search([('type', '=', 'sale')])

        # for id in journal_ids:
        #     journal_id = id
        journals = self.env['account.journal'].search_read([('type','=','sale')])
        journal_id = journals[0]['id']

        invoice_order_ids = self.env['account.move'].search([
            ('partner_id', '=', self.partner_id.id),
            ('state', '=', 'draft'), ('move_type', '=', 'out_invoice')])

        if not invoice_order_ids:
            for record in self:
                vals = {
                        'invoice_origin': record.name,
                        'ref': record.name,
                        'partner_id': record.partner_id.id,
                        'invoice_date': record.date_billing,
                        "user_id": record.user_id.id,
                        "invoice_payment_term_id": record.payment_term_id.id,
                        "currency_id": record.currency_id.id,
                        'move_type':'out_invoice',
                        'journal_id': journal_id
                    }

                invoice_id = self.env['account.move'].sudo().create(vals)

                return invoice_id.id
        else:
            for invoice_order_id in invoice_order_ids:
                invoice_ids.append(invoice_order_id)
            if len(invoice_ids) > 1:
                raise UserError(_('You have more than one open invoice quotations for {}.'.format(self.partner_id.name)))
            else:
                invoice_id = invoice_order_ids.id
                return invoice_id

    def _action_post_invoice_lines(self):
        '''Post order lines to invoice lines'''

        order_nos = []
        lines = []

        invoice_id = self._get_invoice_document_ids()

        if not invoice_id:
            raise UserError(_('An error occured, could not obtain a invoice id'))

        for record in self:
            # invoice_order_line_ids = self.env['account.move.line'].search([
            #     ('move_id', '=', invoice_id)])
            # if invoice_order_line_ids:
            #     for invoice_order_line_id in invoice_order_line_ids:
            #         order_nos.append(invoice_order_line_id.order_no)

            for order_id in record.order_line:
                line_vals = (0, 0, {    
                    "product_id": order_id.product_id.id,
                    "name": order_id.name,
                    "quantity": order_id.quantity,
                    "order_no": record.reference_number,
                    "dates": self.date_billing,
                    "price_unit": order_id.price_unit,
                    "move_id": invoice_id,
                    # "account_id": account_id.id
                })
                _logger.info('++++---- {0}'.format(line_vals))
                
                lines.append(line_vals)
                # if record.reference_number not in order_nos:
                #     lines.append(line_vals)
                #     _logger.info('++++----++++ {0}'.format(lines))

        # for line in lines:
        try:
            move_id = self.env['account.move'].search([('id', '=', invoice_id),
                ('move_type', '=', 'out_invoice'), ('state', '=', 'draft')])
            move_id.update({'ref': move_id.ref + '/' + self.name,'invoice_line_ids': lines})
            # move_id.action_post()
                
        except Exception as error:
            raise UserError(error)

    def _action_remove_lines_from_draft_invoice(self):
        order_nos = []

        for record in self:
            for order_line in record.order_line:
                order_nos.append(order_line.origin)

        if order_nos is not None:
            for order_no in order_nos:
                account_move_domain = [
                    ('invoice_line_ids.order_no', '=', order_no),
                    ('move_type', '=', 'out_invoice')]

                invoice_record = self.env['account.move'].search(account_move_domain)

                if invoice_record.state != 'draft':
                    raise UserError('This record has already been invoiced or does not exist!')

                for move_line in invoice_record.invoice_line_ids:
                    if move_line.order_no == order_no:
                        try:
                            self.env['account.move.line'].search([('id', '=', move_line.id)]).remove()
                            # move_line.unlink()
                            # invoice_record.(move_line)
                            self.update({'status': 'cancel'})
                        except Exception as e:
                            raise UserError(_(e))

    @api.onchange('vehicle_id')
    def _autopupulate_fields(self):
        for record in self:
            return record.update({'partner_id': record.vehicle_id.carrier_id})

