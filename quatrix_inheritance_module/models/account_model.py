import logging
import base64
from odoo import models, fields, api, _
from odoo.exceptions import UserError
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

    def action_post(self):
        '''Require Certificate number for KBL'''
        res = super(AccountMove, self).action_post()

        for record in self:
            if record.partner_id.require_certificate_number:
                if not record.certificate_number:
                    raise UserError(_("Please provide a certificate number."))
        self.create_journals_from_client_debits()
        return res
    
    def button_draft(self):
        '''Restrict reset on confirmed entries with '''
        res = super(AccountMove, self).button_draft()

        for record in self:
            if record.customer_debits and record.type == 'posted':
                raise UserError("Unauthorized action! Cannot reset a posted entry with deductions.")
        return res
    
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

        account_recievable = self.env['account.account'].search([('code', '=', '121000')])
        account_payable = self.env['account.account'].search([('code', '=', '211000')])

        for record in self:
            # for line in record.line_ids:
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

            for move in new_move_id:
                for move_line in move.line_ids:
                    if move_line.account_id == account_payable:
                        move_id.js_assign_outstanding_line(move_line.id)
                    if move_line.account_id == account_recievable:
                        record.js_assign_outstanding_line(move_line.id)
            self._update_customer_debits_billing_state()

    @api.depends("customer_debits")
    def _compute_debit_amount(self):
        '''Compute total debit amount for pending invoice'''
        self._check_if_billing_order_already_selected()

        totals = 0
        for record in self:
            for debit in record.customer_debits:
                totals += debit.amount_total
            record.customer_debit_amount = totals
    
    @api.onchange('state', 'payment_state')
    def _update_customer_debits_billing_state(self):
        '''Update billing state on billing order if invoice state is paid'''

        for record in self:
            for customer_debit in record.customer_debits:
                bills = self.env["billing.order"].search([("id","=",customer_debit.id)])

                for bill in bills:
                    bill.update({'billing_client_state' : 'paid'})
    
    def _check_if_billing_order_already_selected(self):
        '''Check if a billing order already exists within the accounting system to avoid double entry'''        
        # moves = self.env['account.move'].search([('payment_state','!=','paid'), ('partner_id', '=', self.partner_id.id)])
        debits = []

        for move in self.filtered(lambda m: m.payment_state != 'paid'):
            for debit in move.customer_debits:
                if debit.name is False:
                    return
                debits.append(debit.name)
        for record in self:
            for debit_rec in record.customer_debits:
                count = debits.count(debit_rec.name)
                if count > 1:
                    raise UserError("A client debit that already exists has been selected.")
    
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
