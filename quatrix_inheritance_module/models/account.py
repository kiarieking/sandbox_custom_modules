from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.misc import formatLang

import logging
import base64
import json
from datetime import datetime
import cloudinary
import cloudinary.uploader
import PyPDF2
from os import getenv
from io import BytesIO
from PIL import Image


_logger = logging.getLogger(__name__)

API_KEY = getenv('cloudinary_api_key')
API_SECRET = getenv('cloudinary_api_secret')
NAME = getenv("cloudinary_name")


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    additional_charges = fields.Float(related="sale_line_ids.additional_charges", readonly=False, string="Charges")
    order_no = fields.Char(related="sale_line_ids.order_no", required=False, readonly=False, store=True, string="Delivery No.")
    dates = fields.Date(related="sale_line_ids.date", readonly=False, store=True, string="Dispatch Date")
    notes = fields.Text(related='sale_line_ids.notes', readonly=False, string="Lines")
    
    
class AccountMove(models.Model):
    _inherit = 'account.move'

    file_name = fields.Char(string="File Name")
    certificate_number = fields.Char(string="Certificate Number", readonly=False)
    partner_type = fields.Char(string="Partner Type", default=False)
    customer_debits = fields.Many2many("billing.order", string="Client Debits", readonly=False)
    customer_debit_amount = fields.Float("Client Debit", default=0, compute="_compute_debit_amount", store=True)
    invoice_upload = fields.Binary(string="Invoice Upload")
    invoice_upload_link = fields.Char(string="Invoice Uploads Link",
        compute="_upload_to_cloudinary", store=True, default=False)
    invoice_upload_link_id = fields.Char(store=True)
    temp_field = fields.Char("Temp", compute="_compute_partner_type")
    partner_ids = fields.Many2many("res.partner", string="Journal Items Partners", compute="_compute_journal_items_partners")
    deduction_line_ids = fields.One2many('account.deduction.line', 'deduction_id')
    deduction_amount_total = fields.Float("Deductions", default=0.0, compute="_compute_deduction_amount")
    amount_to_deduct = fields.Float(related="deduction_line_ids.amount_to_deduct")
    
    def resize_documents(self):
        '''Autocompress pdf documents'''
        for record in self:
            input_ = PyPDF2.PdfFileReader(BytesIO(base64.b64decode(record.invoice_upload)))
            output = PyPDF2.PdfFileWriter()
            outIO = BytesIO()

            for p_nr in range(input_.getNumPages()):

                page = input_.getPage(p_nr)
                outPage = output.addBlankPage(595, 841)
                outPage.mergePage(page)
                outPage.compressContentStreams()

            output.write(outIO)
            outIO.seek(0)

            encoded_string = base64.b64encode(outIO.read())

            return encoded_string

    def resize_files(self):
        '''Autocompress images'''
        for record in self:
            upload = BytesIO(base64.b64decode(record.invoice_upload))

            image = Image.open(upload)
            image.resize((128, 128), Image.ANTIALIAS)
            output = BytesIO()

            image.save(output, format="JPEG", optimize=True, quality=20)

            output.seek(0)
            encoded_string = base64.b64encode(output.read())

            return encoded_string
            
    @api.depends('line_ids.amount_currency', 'line_ids.tax_base_amount', 'line_ids.tax_line_id', 'partner_id', 'currency_id', 'amount_total', 'amount_untaxed')
    def _compute_tax_totals_json(self):
        """ Computed field used for custom widget's rendering.
            Only set on invoices.
        """
        for move in self:
            if not move.is_invoice(include_receipts=True):
                # Non-invoice moves don't support that field (because of multicurrency: all lines of the invoice share the same currency)
                move.tax_totals_json = None
                continue

            tax_lines_data = move._prepare_tax_lines_data_for_totals_from_invoice()
            
            tax_totals = self._get_tax_totals(move.partner_id, tax_lines_data, move.amount_total, move.amount_untaxed, move.currency_id)
            
            tax_totals['generics'] = [{
                'name': 'Client Debit',
                'amount': move.customer_debit_amount,
                'formatted_amount': formatLang(self.env, move.customer_debit_amount, currency_obj=move.currency_id),
            }, {
                'name': 'Deductions',
                'amount': move.deduction_amount_total,
                'formatted_amount': formatLang(self.env, move.deduction_amount_total, currency_obj=move.currency_id),
            }]

            move.tax_totals_json = json.dumps({
                **tax_totals,
                'allow_tax_edition': move.is_purchase_document(include_receipts=False) and move.state == 'draft',
            })  
                
    @api.depends('amount_to_deduct')
    @api.onchange('amount_to_deduct')
    def _compute_deduction_amount(self):
        '''Compute deduction amount total'''        
        for move in self:          
            move.deduction_amount_total = sum(d.amount_to_deduct for d in move.deduction_line_ids)
    
    @api.depends('partner_id', 'partner_type')
    def _compute_partner_type(self):
        '''
        Check whether the partner is a customer or vendor
        Use temp field to run computation on depends due to store=True issue on already existing fields issue in Odoo
        '''

        invs = self.env['account.move'].search([('partner_type','not in', ['Customer', 'Vendor'])])

        for inv in invs:
            if inv.partner_id.is_customer:
                inv.partner_type= "Customer"
                inv.temp_field = "Customer"
            if inv.partner_id.is_vendor:
                inv.partner_type= "Vendor"

        self.temp_field = "computation done"
    
    @api.depends('line_ids')
    def _compute_journal_items_partners(self):
        for entry in self:
            entry.partner_ids = entry.line_ids.partner_id.ids
    
    @api.depends("customer_debits")
    def _compute_debit_amount(self):
        '''Compute total debit amount for pending invoice'''
        self._check_if_billing_order_already_selected()
            
        for move in self:
            move.customer_debit_amount = sum(bill.amount_total for bill in move.customer_debits)
            
            
    @api.depends(
        'customer_debit_amount',
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state'
        )
    def _compute_amount(self):
        '''Compute amount residual'''
        
        res = super(AccountMove, self)._compute_amount()

        invoice_ids = [move.id for move in self if move.id and move.is_invoice(include_receipts=True)]
        self.env['account.payment'].flush(['state'])

        if invoice_ids:
            # DEPRECATED:: payment.state IN ('posted', 'sent') AND journal.post_at = 'bank_rec' no longer supported
            self._cr.execute(
                '''
                    SELECT move.id
                    FROM account_move move
                    JOIN account_move_line line ON line.move_id = move.id
                    JOIN account_partial_reconcile part ON part.debit_move_id = line.id OR part.credit_move_id = line.id
                    JOIN account_move_line rec_line ON
                        (rec_line.id = part.debit_move_id AND line.id = part.credit_move_id)
                    JOIN account_payment payment ON payment.id = rec_line.payment_id
                    JOIN account_journal journal ON journal.id = rec_line.journal_id
                    WHERE move.id IN %s
                UNION
                    SELECT move.id
                    FROM account_move move
                    JOIN account_move_line line ON line.move_id = move.id
                    JOIN account_partial_reconcile part ON part.debit_move_id = line.id OR part.credit_move_id = line.id
                    JOIN account_move_line rec_line ON
                        (rec_line.id = part.credit_move_id AND line.id = part.debit_move_id)
                    JOIN account_payment payment ON payment.id = rec_line.payment_id
                    JOIN account_journal journal ON journal.id = rec_line.journal_id
                    WHERE move.id IN %s
                ''', [tuple(invoice_ids), tuple(invoice_ids)]
            )
            in_payment_set = set(res[0] for res in self._cr.fetchall())
        else:
            in_payment_set = {}


        for move in self:

            cust_debit = move.customer_debit_amount
            
            total_untaxed = 0.0
            total_untaxed_currency = 0.0
            total_tax = 0.0
            total_tax_currency = 0.0
            total_to_pay = 0.0
            total_residual = 0.0
            total_residual_currency = 0.0
            total = 0.0
            total_currency = 0.0
            currencies = move._get_lines_onchange_currency().currency_id

            for line in move.line_ids:
                if move.is_invoice(include_receipts=True):
                    # === Invoices ===

                    if not line.exclude_from_invoice_tab:
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency - cust_debit
                    elif line.tax_line_id:
                        # Tax amount.
                        total_tax += line.balance
                        total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.account_id.user_type_id.type in ('receivable', 'payable'):
                        # Residual amount.
                        # line.amount_residual -= cust_debit
                        total_to_pay += line.balance
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

            if move.move_type == 'entry' or move.is_outbound():
                sign = 1
            else:
                sign = -1
            move.amount_untaxed = sign * (total_untaxed_currency if len(currencies) == 1 else total_untaxed)
            move.amount_tax = sign * (total_tax_currency if len(currencies) == 1 else total_tax)
            move.amount_total = sign * (total_currency if len(currencies) == 1 else total)
            move.amount_residual = -sign * (total_residual_currency if len(currencies) == 1 else total_residual)
            move.amount_untaxed_signed = -total_untaxed
            move.amount_tax_signed = -total_tax
            move.amount_total_signed = abs(total) if move.move_type == 'entry' else -total
            move.amount_residual_signed = total_residual

            # Apply Customer Debit
            # move.amount_total -= cust_debit
            # move.amount_total_signed -= cust_debit
            # move.amount_residual -= cust_debit
            # move.amount_residual_signed -= cust_debit

            currency = len(currencies) == 1 and currencies or move.company_id.currency_id
            is_paid = currency and currency.is_zero(move.amount_residual) or not move.amount_residual

             # Compute 'payment_state'.
            if move.move_type == 'entry':
                move.payment_state = False
            elif move.state == 'posted' and is_paid:
                # self._update_customer_debits_billing_state()

                if move.id in in_payment_set:
                    move.payment_state = 'in_payment'
                else:
                    move.payment_state = 'paid'
                    
            else:
                move.payment_state = 'not_paid'
        

        return res
    
    @api.depends('invoice_upload')
    def _get_default_code(self):
        '''Return default code to be used in cloudinary'''
        code = None
        for record in self:
            if not record.partner_id.name:
                raise UserError(_('Please enter the vendor/customer.'))
            code = record.partner_id.name
        return code

    @api.depends('invoice_upload')
    def _upload_to_cloudinary(self):
        '''Upload Image to cloudinary'''
        
        for move in self:
            if not move.invoice_upload:
                return
        
            cloudinary.config(cloud_name=NAME, api_key=API_KEY,api_secret=API_SECRET)

            base_file = None
            default_code = move._get_default_code()

            for record in move:

                if not record.file_name:
                    return "Nada"
                if not record.partner_id.name:
                    raise UserError(_('You dont have any products added in this document.'))

                extension = record.file_name.split(".")[1]
                file_name = record.file_name.split(".")[0]

                encoded_string = None

                try:
                    if extension.lower() == 'pdf':
                        encoded_string = move.resize_documents()
                        # encoded_string = base64.b64encode(record.file_name)
                    else:
                        encoded_string = move.resize_files()

                    base_file = "data:image/%s;base64,"%extension + (encoded_string).decode('utf-8')

                except Exception as e:
                    raise UserError(str(e))

                date_transformed = datetime.now()

                formatted_date= datetime.strftime(date_transformed, "%Y%m%d")
                formatted_time= datetime.strftime(date_transformed, "%H%M%S")

                format_name = datetime.strftime(date_transformed, "%Y-%m")
                folder_name = "Quatrix-InvoiceUploads-"+format_name

                try:
                    full_file_name = "D"+formatted_date+"." + "T"+ formatted_time +"." + default_code + "." + file_name
                except:
                    raise UserError("Please ensure that all the products entered have an internal reference.")

                if record.invoice_upload_link and record.invoice_upload_link_id:
                    resp = cloudinary.uploader.destroy(str(record.invoice_upload_link_id))
                    response = cloudinary.uploader.upload(base_file, folder=folder_name, public_id=full_file_name, overwrite=True)
                    record.update({ "invoice_upload_link": response['secure_url']})
                    record.update({ "invoice_upload_link_id": response["asset_id"]})
                if not record.invoice_upload_link_id:
                    try:
                        response = cloudinary.uploader.upload(base_file, folder=folder_name, public_id=full_file_name, overwrite=True)
                        record.update({ "invoice_upload_link": response['secure_url']})
                        record.update({ "invoice_upload_link_id": response["asset_id"]})
                    except Exception as Error:
                        print(Error) 
                        
    @api.onchange('state', 'payment_state')
    def _update_customer_debits_billing_state(self):
        '''Update billing state on billing order if invoice state is paid'''
        customer_debit_ids = [d.id for d in self.customer_debits]
        bills = self.env['billing.order'].search([('id', 'in', customer_debit_ids)])
        
        # bills.update({'billing_client_state': 'paid'})       
        [bill.update({'billing_client_state': 'paid'}) for bill in bills]           
    
    @api.onchange('invoice_line_ids')
    def populate_deduction_lines(self):
        '''Populate deductions lines with fuel data when a new supplier invoice is created'''
        self.ensure_one()

        if self.move_type != 'in_invoice':
            return

        order_nos = [line.order_no for line in self.invoice_line_ids]
        
        dispatch_lines = self.env['quatrix.dispatch.line'].search([('order_no', 'in', order_nos)])
        dispatch_names = dispatch_lines.mapped('order_id.name')
        vouchers = self.env['fuel.voucher'].search([('reference_number', 'in', dispatch_names)])
        fuel_names = vouchers.mapped('name')
        
        fuel_invoices = self.env['account.move'].search([('move_type','=','out_invoice'),('partner_id','=', self.partner_id.id), \
            ('ref','in',fuel_names), ('amount_residual','>',0)])
        
        if not fuel_invoices:
            return
                 
        lines = [(0,0, {
            "date_deduction": line.dates,
            "invoice_to_deduct": line.move_id.id,
            "amount_to_deduct": line.move_id.amount_residual,
            'amount_pending': line.move_id.amount_total
        }) for line in fuel_invoices.invoice_line_ids]
        
        self.deduction_line_ids = lines
        
    def button_draft(self):
        '''Restrict reset on confirmed entries with '''
        self.ensure_one()
        settlements = []
        
        # for record in self:
        #     move_names = [record.name]
            
        #     if record.customer_debits and record.type == 'posted':
        #         raise UserError("Unauthorized action! Cannot reset a posted entry with deductions.")
            
        #     move_names += [d.invoice_to_deduct.name for deduction in record.deduction_line_ids for d in deduction]
            
        #     journals = record.env['account.move'].search([('move_type','=','entry'),('ref','in', move_names), ('state', '!=', 'cancel')])
                        
        #     if journals: raise UserError("Unauthorized. A journal exists for the deductions made for this record!")
        
        payments_vals = self.sudo()._get_reconciled_info_JSON_values()  
        settlements += self.env['account.move'].browse([payment['move_id'] for payment in payments_vals]).filtered(lambda m: m.move_type == 'entry')        
        if settlements:
            for misc in settlements:
                _logger.info(f"Reconciled entries: {self.name, self.id} with misc entry {misc.name, misc.id}")
                misc.button_draft()
            
        return super(AccountMove, self).button_draft()
        
    def action_cancel(self):
        '''Restrict deletion of records with active deduction journal entries'''
        self.ensure_one()
        settlements = []
        
        # journals = self.env['account.move'].search([('move_type','=','entry'),('ref','=',self.name), ('state', '!=', 'cancel')])
        # if journals:
        #     raise UserError("Unauthorized. A journal exists for the deductions made for this record!")
        
        payments_vals = self.sudo()._get_reconciled_info_JSON_values()            
        settlements += self.env['account.move'].browse([payment['move_id'] for payment in payments_vals]).filtered(lambda m: m.move_type == 'entry')
        if settlements:
            for misc in settlements:
                misc.action_cancel()                
                    
        return super(AccountMove, self).action_cancel()
    
    def action_post(self):
        '''Require Certificate number for KBL'''
        moves = super(AccountMove, self).action_post()
        
        if self.filtered(lambda m: m.state == 'cancel'): return moves
        
        if self.filtered(lambda m: m.partner_id.require_certificate_number and not m.certificate_number):
            raise UserError(_("Please provide a certificate number."))            
                        
        self.create_journals_from_client_debits()               
        self._check_amount_before_deduction()
        self._do_moves_settlement()
        for move in self: move._misc_entry_settlement()
        
        return moves
    
    def _check_amount_before_deduction(self):
        '''Check if amount to be deducted is greater than invoice amount.'''
        for record in self:
            if record.deduction_amount_total > record.amount_total:
                raise UserError("Deduction cannot be greater than amount total.")
    
    def _do_moves_settlement(self):
        account = self.env['account.account'].search([])
        account_recievable = account.filtered(lambda a: a.code == '121000')
        account_payable = account.filtered(lambda a: a.code == '211000')
        
        due_invoices = self.env['account.move'].search([
            ('move_type','=','out_invoice'),
            ('state','=','posted'),
            ('partner_id','=',self.partner_id.id),
            ('amount_residual', '>', 0),
        ])
        deduction_lines = self.deduction_line_ids.filtered(lambda a: not a.is_settled)        
        
        for deduct in deduction_lines:
            
            due_invoice = due_invoices.filtered(lambda m: m.name == deduct.invoice_to_deduct.name)            
            if not due_invoice: return
            
            vals = [(0, 0, {
                'invoice_to_deduct': self.id,
                'amount_to_deduct': deduct.amount_to_deduct,
                'amount_pending': due_invoice.amount_residual,
                'description': f'payment from {self.name}',
                'is_settled': True,
            })]
            due_invoice.write({'deduction_line_ids': vals})                    
                        
            to_settle_move = deduct.invoice_to_deduct
            debits = {
                'name': deduct.deduction_id.name,
                'debit': abs(deduct.amount_to_deduct),
                'credit': 0.0,
                'partner_id': deduct.deduction_id.partner_id.id,
                'account_id': account_payable.id,
            }
            credits = {
                'name': to_settle_move.name,
                'debit': 0.0,
                'credit': abs(deduct.amount_to_deduct),
                'partner_id': deduct.deduction_id.partner_id.id,
                'account_id': account_recievable.id,
            }
            miscellaneous_move_vals = {
                'move_type': 'entry',
                'journal_id': 3,
                'ref': to_settle_move.name,
                'date': self.date,
                'state': 'draft',
                'line_ids': [(0, 0, debits), (0, 0, credits)]
            }
            
            miscellaneous_move = self.env['account.move'].create(miscellaneous_move_vals)
            miscellaneous_move.action_post()            
            
            for move in miscellaneous_move:
                for move_line in move.line_ids:
                    if move_line.account_id == account_payable:
                        self.js_assign_outstanding_line(move_line.id)
                    if move_line.account_id == account_recievable:
                        to_settle_move.js_assign_outstanding_line(move_line.id)
                        
            deduct.is_settled = True
                        
    # TODO:: perform debits & credits reconciliation for moves reset to (draft/cancel) which had previously been settled
    def _misc_entry_settlement(self):
        self.ensure_one()
        
        move_misc_entries = self.env['account.move'].search([('state', '=', 'draft'), ('move_type', '=', 'entry'), \
            ('line_ids.partner_id', '=', self.partner_id.id), ('line_ids.name', '=', self.name)])
                
        move_misc_entries._post()
        
        recievable_line_ids = move_misc_entries.line_ids.filtered(lambda a: a.account_id.code == '121000')
        payable_line_ids = move_misc_entries.line_ids.filtered(lambda a: a.account_id.code == '211000')
        
        _logger.info(f"Misc Entries: {move_misc_entries} Recievables: {[(r.move_id.name, r.name) for r in recievable_line_ids]} payables: {[(p.move_id.name, p.name) for p in payable_line_ids]}")
        
        for move_line in payable_line_ids: self.js_assign_outstanding_line(move_line.id)
        for move_line in recievable_line_ids:
            invoice = move_line.move_id.search([('name', '=', move_line.name)])
            invoice.js_assign_outstanding_line(move_line.id)
    
    def _check_if_billing_order_already_selected(self):
        '''Check if a billing order already exists within the accounting system to avoid double entry'''        
        # moves = self.env['account.move'].search([('payment_state','!=','paid'), ('partner_id', '=', self.partner_id.id)])
        debits = []
        not_paid = self.filtered(lambda m: m.payment_state != 'paid')
        # debits = [d.name for m in not_paid for d in m.customer_debits if d.name != False]

        for move in not_paid:
            for debit in move.customer_debits:
                if debit.name is False:
                    return
                debits.append(debit.name)
        for record in self:
            for debit_rec in record.customer_debits:
                count = debits.count(debit_rec.name)
                if count > 1:
                    raise UserError("A client debit that already exists has been selected.") 
                
    def create_journals_from_client_debits(self):
        '''Create vendor bills and journals for client debits'''

        for record in self:
            if record.move_type == 'out_invoice':
                if record.customer_debits:
                    for cust_order in record.customer_debits:
                        # Create a bill for shippers
                        journals = self.env['account.journal'].search_read([('type','=','purchase')])
                        journal_id = journals[0]['id']
                        account_payable = self.env['account.account'].search([('code', '=', '500000')])

                        for order_id in cust_order.order_line:
                            line_vals = [(0, 0, {    
                                "product_id": order_id.product_id.id,
                                "name": order_id.name,
                                "quantity": order_id.quantity,
                                "order_no": cust_order.reference_number,
                                "dates": cust_order.date_billing,
                                "price_unit": order_id.price_unit,
                                "account_id": self.env['account.account'].search([('user_type_id', '=', self.env.ref('account.data_account_type_expenses').id)], limit=1).id})]

                            vals = {
                                'invoice_origin': record.name,
                                'ref': cust_order.name,
                                'partner_id': record.partner_id.id,
                                'invoice_date': cust_order.date_billing,
                                "user_id": record.user_id.id,
                                "invoice_payment_term_id": cust_order.payment_term_id.id,
                                # "currency_id": record.currency_id.id,
                                'move_type':'in_invoice',
                                'journal_id': journal_id,
                                'invoice_line_ids': line_vals
                            }

                            move_id = self.env['account.move'].sudo().create(vals)
                            move_id.action_post()
                            self._create_journals_for_created_move_ids(move_id)
    
    def _create_journals_for_created_move_ids(self, move_id):
        '''Create journals and assign'''
        account = self.env['account.account'].search([])
        account_recievable = account.filtered(lambda a: a.code == '121000')
        account_payable = account.filtered(lambda a: a.code == '211000')

        for record in self:
            debit_vals = {
                'name': record.name,
                'debit': 0.0,
                'credit': abs(move_id.amount_total),
                'partner_id': move_id.partner_id.id,
                'account_id': account_recievable.id,
            }

            credit_vals = {
                'name': move_id.name,
                'debit': abs(move_id.amount_total),
                'credit': 0.0,
                'partner_id': move_id.partner_id.id,
                'account_id': account_payable.id,
            }

            vals = {
                'move_type': 'entry',
                'journal_id': move_id.journal_id.id,
                'ref': record.name,
                'date': move_id.date,
                'state': 'draft',
                'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
            }

            new_move_id = self.env['account.move'].create(vals)
            new_move_id.post()

            for move_line in new_move_id.line_ids:
                if move_line.account_id == account_payable:
                    move_id.js_assign_outstanding_line(move_line.id)
                if move_line.account_id == account_recievable:
                    record.js_assign_outstanding_line(move_line.id)
                    
            self._update_customer_debits_billing_state()