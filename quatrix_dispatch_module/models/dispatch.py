# -*- coding: utf-8 -*-
'''Dispatch orders Model'''
import base64
from itertools import product
import PyPDF2
from os import getenv
from io import BytesIO
from PIL import Image
from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv
import cloudinary
import cloudinary.uploader
import phonenumbers, re
from odoo import models, fields, api, _
from odoo.addons.product.models.product_pricelist import Pricelist
from odoo.exceptions import UserError

load_dotenv(find_dotenv())

API_KEY = getenv('cloudinary_api_key')
API_SECRET = getenv('cloudinary_api_secret')
NAME = getenv("cloudinary_name")

class Dispatch(models.Model):
    '''Dispatch Order class'''
    _name = 'quatrix.dispatch'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'quatrix.dispatch'
    _order = 'name desc'

    date_dispatch = fields.Datetime(string="Dispatch Date", required=True, default = lambda self: fields.datetime.now())
    date_delivery = fields.Datetime(string="Delivery Date")
    driver_phone_number = fields.Char(string="Driver Phone Number")
    vehicle_id = fields.Many2one('fleet.vehicle',
        string="Vehicle Registration", ondelete="restrict",required=True)
    name = fields.Char(string='Quotation Number', required=True,
        copy=False, readonly=True, index=True, default=lambda self: _('New'))
    amount = fields.Float(string='Amount Total', compute='_compute_total_amount')
    carrier_charges = fields.Float(string='Carrier Charges', compute='_compute_total_amount')
    loading_charges = fields.Float(string='Loading Charges', default=0.0)
    currency_id = fields.Many2one('res.currency', 'Currency', compute='_compute_currency_id')
    user_id = fields.Many2one('res.users', compute="_get_current_user", string='Staff',
        ondelete="restrict", default=lambda self: self.env.user)
    order_ids = fields.One2many('quatrix.dispatch.line', 'order_id')
    vendor_id = fields.Many2one('res.partner', string="Carrier/Subcon",
        required=True, change_default=True, index=True, tracking=True, compute="_get_vendor")
    partner_id = fields.Many2one('res.partner', string="Customer(Shipper)",
        required=True, change_default=True, index=True, tracking=True,)
    partner_invoice_id = fields.Many2one(
        'res.partner', string='Invoice Address',
        readonly=True,
        states={'draft': [('readonly', False)],
            'order': [('readonly', False)], 'posted': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)
    partner_shipping_id = fields.Many2one(
        'res.partner', string='Delivery Address', readonly=True,
        states={'draft': [('readonly', False)],
            'order': [('readonly', False)], 'posted': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)
    company_id = fields.Many2one('res.company', 'Company',
        required=True, index=True, default=lambda self: self.env.company)
    pod_link = fields.Char(string="Proof Of Delivery Link",
        compute="_upload_to_cloudinary", store=True, default=False)
    purchase_id = fields.Many2one('purchase.number', string="PO Number")
    pod_upload = fields.Binary(string="Proof of delivery")
    file_name = fields.Char(string="File Name")
    pod_link_id = fields.Char(store=True)
    fuel_voucher_count = fields.Char("Fuel Orders", compute="get_fuel_orders")
    breakages_count = fields.Char("Breakages", compute="get_breakages")
    sale_doc = fields.Char("Sale Document", default=False, compute="_get_sale_doc")
    inv_doc = fields.Char("Invoice Document",default=False, compute="_get_invoice_doc")
    inv_status = fields.Char("Invoice Status",default=False, compute="_get_invoice_doc")
    vendor_bill_doc = fields.Char("Vendor Bill Document", default=False, compute="_get_vendor_bill_doc")
    pricelist_id = fields.Many2one('product.pricelist', string="Pricelist")
    order_no = fields.Char(related="order_ids.order_no")


    status = fields.Selection(
        [('draft', "Quotation"),('order', "Dispatch Order"),
        ('posted', "Posted") , ('cancel', "Cancelled")], default='draft')

    @api.depends()
    def _get_current_user(self):
        '''Return active user'''
        self.update({'user_id' : self.env.user.id})

    @api.model
    def create(self, vals):
        '''Create a new dispatch and create a new sequence number'''

        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('dispatch.order') or _('New')
        result =super(Dispatch, self).create(vals)

        result.validate_mobile()
        # result.check_existing_orders()
        result.find_orphan_fuel_vouchers()

        return result

    def write(self, vals):
        '''Check for valid numbers on write'''

        result =super(Dispatch, self).write(vals)

        self.validate_mobile()
        # self.check_existing_orders()
        self.find_orphan_fuel_vouchers()

        return result

    @api.depends('order_ids.amount')
    def _compute_total_amount(self):
        '''Calculate total amount from order lines'''

        for record in self:
            amount_total = 0.0
            carrier_charges = 0.0
            for line in record.order_ids:
                amount_total += line.amount
                carrier_charges += line.carrier_price
            record.update({'amount': amount_total })
            record.update({'carrier_charges': carrier_charges })

    @api.depends()
    def _compute_currency_id(self):
        '''Return active company currency, expected KSH'''

        for record in self:
            if record.partner_id.property_product_pricelist and record.partner_id.property_product_pricelist.id:
                pricelist = record.pricelist_id = record.partner_id.property_product_pricelist.id
                record.currency_id = record.env['product.pricelist'].browse(pricelist).currency_id.id
            else:
                record.currency_id = record.env.user.company_id.sudo().currency_id.id

    def action_post(self):
        '''Create sale documents or append sale order lines in an open quotation exists'''

        if not self.pod_link:
            raise UserError(_('Please input a link to the proof of delivery to post.'))
        
        self._action_post_quotation_lines()

    def action_confirm(self):
        '''Confirm an order'''

        if not self.pod_link:
            raise UserError(_('Please input a link to the proof of delivery to confirm.'))

        self._action_post_purchase_lines()
    
    def action_reset(self):
        '''Reset an order to quotations by updating the status of the order to draft'''

        self.update({'status' : 'draft'})

    def action_cancel(self):
        '''Cancel a dispatch order'''

        order_nos = []

        for record in self:
            for order_line in record.order_ids:
                order_nos.append(order_line.order_no)

        if order_nos is not None:
            for order_no in order_nos:
                sale_record = self.env['sale.order'].search([
                    ('order_line.order_no', '=', order_no),
                    ('state', '=', 'draft')])

                purchase_record = self.env['carrier.order'].search([
                    ('order_no', '=', order_no),
                    ('status', '=', 'draft')])
                
                if sale_record is None:
                    raise UserError('This record has already been invoiced or does not exist')

                try:
                    for order_line in sale_record.order_line:
                        if order_line.order_no == order_no:
                            self.env['sale.order.line'].search([('id', '=', order_line.id)]).unlink() or sale_record.unlink(order_line.id)
                            self.update({'status': 'cancel'})

                    if purchase_record.order_no == order_no:
                        self.env['carrier.order'].search([('id', '=', purchase_record.id)]).unlink() or purchase_record.unlink(purchase_record.id)
                        self.update({'status': 'cancel'})
                except Exception as e:
                    raise UserError(_(e))

    def _get_sale_document_id(self):
        '''Get sale id from an open sale order or create a sale id if a sale id doesn't exist'''
        
        sale_ids = []

        sale_order_ids = self.env['sale.order'].search([
            ('partner_id', '=', self.partner_id.id),
            ('state', '=', 'draft')])

        if not sale_order_ids:
            for record in self:
                vals = {
                        'partner_id': record.partner_id.id,
                        'validity_date': record.date_delivery,
                        "user_id": record.user_id.id,
                    }

                sale_id = self.env['sale.order'].sudo().create(vals)

                return sale_id.id
        else:
            for sale_order_id in sale_order_ids:
                sale_ids.append(sale_order_id)
            if len(sale_ids) > 1:
                raise UserError(_('You have more than one open sale quotations for {}.'.format(self.partner_id.name)))
            else:
                sale_id = sale_order_ids.id
                return sale_id

    def _action_post_quotation_lines(self):
        '''Post dispatch order lines to an sale quotation lines'''

        lines = []
        order_nos = []

        sale_id = self._get_sale_document_id()

        if not sale_id:
            raise UserError(_('An error occured, could not obtain a sale id'))

        sale_order_line_ids = self.env['sale.order.line'].search([('order_id', '=', sale_id)])

        for sale_order_line_id in sale_order_line_ids:
            order_nos.append(sale_order_line_id.order_no)

        for record in self:
            for order_id in record.order_ids:
                line_vals = [(0, 0, {
                    "date": record.date_dispatch,
                    "order_no": order_id.order_no,
                    "product_id": order_id.product_id.id,
                    'product_uom' : order_id.product_id.uom_id.id,
                    "name": (record.vehicle_id.license_plate + ":" + order_id.description) or record.vehicle_id.license_plate,
                    "notes": order_id.notes,
                    "product_uom_qty": order_id.quantity,
                    "price_unit": order_id.price_unit,
                    "order_id": sale_id,
                })]

                lines.append(line_vals)
            sale_id = self.env['sale.order'].search([('id', '=', sale_id)])

            try:
                for line in lines:
                    sale_id.write({ 'order_line': line })
                    self.update({'status' : 'posted'})
            except Exception as error:
                raise UserError(error)

    def _get_purchase_document_id(self):
        '''Get purchase id from an open purchase order or create a purchase id if an open purchase order does not exist'''

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
                        "date_order": record.date_dispatch,
                    }

                purchase_id = self.env['purchase.order'].sudo().create(vals)

                return purchase_id.id
        else:
            for purchase_order_id in purchase_order_ids:
                purchase_ids.append(purchase_order_id)
            if len(purchase_ids) > 1:
                raise UserError(_('You have more than one open purchase quotations for {}.'.format(self.partner_id.name)))
            else:
                purchase_id = purchase_order_ids.id
                return purchase_id
 
    def _action_post_purchase_lines(self):
        '''Function reconfigured to create carrier orders based on the dispatch order lines'''

        for record in self:
            for order_id in record.order_ids:
                
                vals = {
                        "date": record.date_dispatch,
                        "order_no": order_id.order_no,
                        "product_id": order_id.product_id.id,
                        "vehicle_id": record.vehicle_id.id,
                        "vendor_id": record.vendor_id.id,
                        "reference": record.name,
                        "description": (record.vehicle_id.license_plate + ":" + order_id.description) or record.vehicle_id.license_plate,
                        "quantity": order_id.quantity,
                        # "carrier_price": order_id.product_id.standard_price,
                        "carrier_price": order_id.carrier_price
                    }

                try:
                    self.env['carrier.order'].create(vals)
                    self.update({'status' : 'order'})
                except Exception as error:
                    raise UserError(error)


    def resize_documents(self):
        '''Autocompress pdf documents'''
        for record in self:
            input_ = PyPDF2.PdfFileReader(BytesIO(base64.b64decode(record.pod_upload)))
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
        '''Autocompress image uploads'''

        for record in self:
            upload = BytesIO(base64.b64decode(record.pod_upload))

            image = Image.open(upload)
            image.resize((128, 128), Image.ANTIALIAS)
            output = BytesIO()

            image.save(output, format="JPEG", optimize=True, quality=20)

            output.seek(0)
            encoded_string = base64.b64encode(output.read())

            return encoded_string

    @api.depends('pod_upload')
    def _get_default_code(self):
        '''Return product default code to be used in cloudinary file names'''

        code = "default_code"

        for record in self:
            if not record.order_ids:
                pass
            for line in record.order_ids:
                if not line.product_id:
                    raise UserError(_('Please enter product(s) that match the proof of delivery document.'))
                for product in line.product_id:
                    code = product[0].default_code
        return code

    @api.depends('pod_upload')
    def _upload_to_cloudinary(self):
        '''Upload Image to cloudinary'''

        cloudinary.config(cloud_name=NAME, api_key=API_KEY,api_secret=API_SECRET)

        base_file = None
        default_code = self._get_default_code()

        for record in self:

            if not record.file_name:
                return "empty string"

            if not record.order_ids.product_id:
                raise UserError(_('You dont have any products added in this document.'))

            extension = record.file_name.split(".")[1]
            file_name = record.file_name.split(".")[0]

            encoded_string = None

            try:
                if extension.lower() == 'pdf':
                    encoded_string = self.resize_documents()

                else:
                    encoded_string = self.resize_files()

                base_file = "data:image/%s;base64,"%extension + (encoded_string).decode('utf-8')

            except Exception as e:
                raise UserError(str(e))

            date_transformed = datetime.now()

            formatted_date= datetime.strftime(date_transformed, "%Y%m%d")
            formatted_time= datetime.strftime(date_transformed, "%H%M%S")

            format_name = datetime.strftime(date_transformed, "%Y-%m")
            folder_name = "Quatrix-Dispatch-"+format_name

            try:
                full_file_name = "D"+formatted_date+"." + "T"+ formatted_time +"." + default_code + "." + file_name
            except:
                raise UserError("Please ensure that all the products entered have an internal reference.")

            if record.pod_link and record.pod_link_id:
                resp = cloudinary.uploader.destroy(str(record.pod_link_id))
                response = cloudinary.uploader.upload(base_file, folder=folder_name, public_id=full_file_name, overwrite=True)
                record.update({ "pod_link": response['secure_url']})
                record.update({ "pod_link_id": response["asset_id"]})

            if not record.pod_link_id:
                response = cloudinary.uploader.upload(base_file, folder=folder_name, public_id=full_file_name, overwrite=True)
                record.update({ "pod_link": response['secure_url']})
                record.update({ "pod_link_id": response["asset_id"]})


    @api.depends('vehicle_id')
    def _get_vendor(self):
        '''select vendor automatically when selecting a vehicle'''
        for record in self:
            record.update({'vendor_id': record.vehicle_id.carrier_id})
    
    @api.depends('driver_phone_number')
    def validate_mobile(self):
        """ Raise a ValidationError if the value looks like a mobile telephone number."""
        for record in self:
            if record.driver_phone_number:
                if len(record.driver_phone_number) != 13:
                    raise UserError(_("Phone number too short! Please use format +254712345678"))

                phone = phonenumbers.parse(record.driver_phone_number, "KE")
                if (phonenumbers.is_valid_number(phone) or phonenumbers.is_possible_number(phone)):
                    print(phone)
                else:
                    raise UserError("Invalid mobile number %s! Please use format +254712345678"%phone)        
    
    def get_fuel_orders(self):
        '''Get fuel orders related to this dispatch document and return the count'''

        vouchers_count = self.env['fuel.voucher'].search_count([("reference_number", "=", self.name)])
        for record in self:
            record.update({"fuel_voucher_count": vouchers_count})
    
    def get_fuel_voucher(self):
        '''Find an open an existing fuel order or create one if no existing vouchers exist'''

        if self.fuel_voucher_count == '0':
            return self.create_fuel_voucher()
        return self._open_existing_voucher()
  
    def _open_existing_voucher(self):
        '''Find and open existing vouchers'''

        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Fuel Orders',
            'view_mode': 'tree,form',
            'res_model': 'fuel.voucher',
            'domain': [('reference_number', '=', self.name)],
            'context': "{'create': False}"
        }
    
    def create_fuel_voucher(self):
        '''Create a new Fuel Voucher'''
        
        context = {
            'default_reference_number': self.name,
            'default_vehicle_id': self.vehicle_id.id,
            'default_driver_phone_number': self.driver_phone_number
            }

        return {
            'type': 'ir.actions.act_window',
            'name': 'Fuel Orders',
            'view_mode': 'form',
            'res_model': 'fuel.voucher',
            'target':'new',
            'context': context
        }

    def find_orphan_fuel_vouchers(self):
        '''Find open and orphaned fuel vouchers and link them to this dispatch document'''

        dispatch_date = None
        previous_day = None

        references = set()

        for record in self:
            dispatch_date = (record.date_dispatch).strftime("%Y-%m-%d")
            previous_day = (record.date_dispatch - timedelta(days=1)).strftime("%Y-%m-%d")

        fuel_vouchers = self.env['fuel.voucher'].search([
            ('date', '>=', previous_day),
            ('date', '<=', dispatch_date),
            ('vehicle_id', '=', self.vehicle_id.id),
            ])

        for voucher_id in fuel_vouchers:
            voucher_id.reference_number and references.add(voucher_id.reference_number)
        
        if self.name in references:
            return
        
        for voucher_id in fuel_vouchers:
            if not voucher_id.reference_number:
                return voucher_id.update({'reference_number' : self.name})

    def get_breakages(self):
        '''Get Breakages from Billing Order related to this dispatch and return their count on the smart button'''

        breakages_count = self.env['billing.order'].search_count([("reference_number", "=", self.name)])
        for record in self:
            record.update({"breakages_count": breakages_count})

    def action_get_breakages(self):
        '''Smart button function to open existing billing orders or create a new billing order otherwise '''

        if self.breakages_count == '0':
            return self.create_billing_order()
        return self._open_existing_bill()

    def _open_existing_bill(self):
        '''smart button functjion to find and open existing billing orders'''

        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Billing Orders',
            'view_mode': 'tree,form',
            'res_model': 'billing.order',
            'domain': [('reference_number', '=', self.name)],
            'context': "{'create': False}"
        }

    def create_billing_order(self):
        '''smart button functiuon to create a new billing order'''

        context = {
            'default_reference_number': self.name,
            'default_vehicle_id': self.vehicle_id.id,
            # 'default_driver_phone_number': self.driver_phone_number
            }

        return {
            'type': 'ir.actions.act_window',
            'name': 'Billing Orders',
            'view_mode': 'form',
            'res_model': 'billing.order',
            'target':'new',
            'context': context
        }

    # @api.onchange('order_no')
    # def check_existing_orders(self):
    #     '''Confirm if order numbers entered already exist in the database'''

    #     delivery_numbers = [] # Delivery numbers from the current document.
    #     order_numbers = [] # Existing delivery numbers - From the database.

    #     records = self.env['quatrix.dispatch.line'].search([('order_id', '!=', self.id)])

    #     for record in records:
    #         string = record.order_no.split("/")
    #         delivery_no = record.order_no.replace(r";", "/")
    #         delivery_no = delivery_no.replace(r",", "/")
    #         delivery_no = delivery_no.replace(r"#", "/")
    #         string = delivery_no.split("/")

    #         order_numbers.extend(string)

    #     for record in self:
    #         for line in record.order_ids:

    #             delivery_no = line.order_no.replace(r";", "/")
    #             delivery_no = delivery_no.replace(r",", "/")
    #             delivery_no = delivery_no.replace(r"#", "/")
    #             delivery_no = delivery_no.split("/")

    #             delivery_numbers.extend(delivery_no)

    #     for delivery_no in delivery_numbers:
    #         if delivery_no in order_numbers:
    #             raise UserError("The delivery no %s already exists."%delivery_no)

        
    #     # check =  any(item in order_numbers for item in delivery_numbers)

    #     # if check:
    #     #     raise UserError("The delivery no already exists.")

    @api.depends('status', 'name')
    @api.onchange('status')
    def _get_sale_doc(self):
        '''Get the sale document number/name related to this dispatch and update it on the view'''
      
        sale_document_lines = self.env['sale.order'].search([])
        order_no = None
        order_id = None

        for record in self:
            if record.status == 'posted':
                for line in record.order_ids:    
                    order_no = line.order_no
                
                if not order_no:
                    raise UserError("No order number found")
                
                for order_line in sale_document_lines.order_line:
                    if order_line.order_no == order_no:
                        order_id = order_line.order_id
                if order_id:

                    sale_orders = self.env['sale.order'].search([('id', '=', order_id.id)])

                    for sale_order in sale_orders:
                        record.sale_doc = sale_order.name
            else:
                record.sale_doc = ''

    @api.depends('status')
    def _get_invoice_doc(self):
        '''
        Get the invoice document number/name 
        and invoice status related to this dispatch document 
        and update it on view

        This is to assist the user to know whether a particular
        dispatch has been invoiced and whether it has been paid
        '''

        inv_status = 'not_paid'
       
        for record in self:
            if not record.sale_doc or record.sale_doc == '' or record.status != 'posted':
                record.inv_doc = ''
            else:
                invoice_documents = self.env['account.move'].search([('invoice_origin','=',record.sale_doc), ('move_type','=', 'out_invoice')])

                if invoice_documents:
                    for invoice_doc in invoice_documents:
                        record.inv_doc = invoice_doc.name
                        inv_status = invoice_doc.payment_state
                else:
                    record.inv_doc = ''
            record.inv_status = inv_status


    @api.depends('status')
    def _get_vendor_bill_doc(self):
        '''
        Get the supplier invoice document number/name 
        and invoice status related to this dispatch document 
        and update it on view

        This is to assist the user to know whether a particular
        dispatch has been invoiced and whether the sub contractor has been paid
        '''
        
        invoice_id = None
        order_no = None

        for record in self:
            for line in record.order_ids:
                order_no = line.order_no

        inv_lines = self.env['account.move.line'].search([('order_no', '=', order_no)])
        for inv_line in inv_lines:
            invoice_id = inv_line.move_id
        
        if not invoice_id:
            record.vendor_bill_doc = ''
        else:
            for record in self:
                invoice_documents = self.env['account.move'].search([('id','=',invoice_id.id), ('move_type','=', 'in_invoice')])

                if invoice_documents:
                    for invoice_doc in invoice_documents:
                        record.vendor_bill_doc = invoice_doc.name
                else:
                    record.vendor_bill_doc = ''