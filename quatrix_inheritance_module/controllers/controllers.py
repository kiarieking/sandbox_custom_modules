# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import Response, request
import json

class Product(http.Controller):
    '''Handle products'''
    @http.route('/api/products', type='json', auth='api_key', website=False, methods=['GET'])
    def get_products(self):
        products_list = []

        product_ids = request.env['product.product'].sudo().search([])

        for product_id in product_ids:
            data = {
                "id": product_id.id,
                "name": product_id.name,
                "price": product_id.list_price,
                "cost": product_id.standard_price,
                "related_customer_id": product_id.partner_id.carrier_carrier_id,
                "related_customer_name": product_id.partner_id.name,
                "core_product_id": product_id.core_product_id
                }
            products_list.append(data)

        response = {"data": products_list, "message": "Product(s) found"}
        return response

    @http.route('/api/products/<int:id>', type='json', auth='api_key', website=False, methods=['GET'])
    def get_product(self, id=None, **kwargs):
        products_list = []

        product_ids = request.env['product.product'].sudo().search([('id', '=', id)])

        for product_id in product_ids:
            data = {
                "id": product_id.id,
                "name": product_id.name,
                "price": product_id.list_price,
                "cost": product_id.standard_price,
                "related_customer_id": product_id.partner_id.carrier_carrier_id,
                "related_customer_name": product_id.partner_id.name,
                "core_product_id": product_id.core_product_id
                }
            products_list.append(data)

        response = {"data": products_list, "message": "Product(s) found"}
        return response
    
    @http.route('/api/<int:shipper_id>/products', type='json', auth='api_key', website=False, methods=['GET'])
    def get_products_by_shipper_id(self, shipper_id=None, **kwargs):
        # TODO: Impelement get product by shipper ID

        partner = request.env['res.partner'].sudo().search([('core_shipper_id', '=', shipper_id)])
        if not partner.id:
            response = {"data": [], "message": "Product(s) found"}
            return response

        products_list = []

        product_ids = request.env['product.product'].sudo().search([('partner_id', '=', partner.id)])

        for product_id in product_ids:
            data = {
                "id": product_id.id,
                "name": product_id.name,
                "price": product_id.list_price,
                "cost": product_id.standard_price,
                "related_customer_id": product_id.partner_id.carrier_carrier_id,
                "related_customer_name": product_id.partner_id.name,
                "core_product_id": product_id.core_product_id
                }
            products_list.append(data)

        response = {"data": products_list, "message": "Product(s) found"}
        return response

    @http.route('/api/products/<int:id>', type='json', auth='api_key', website=False, methods=['PATCH'])
    def update_product(self, id=None, **kwargs):
        products_list = []

        product_vals = {}

        try:
            product_vals["name"]= kwargs['name']
            product_vals["list_price"]= kwargs['price']
            product_vals["standard_price"]= kwargs['cost']
            product_vals["core_product_id"]= kwargs['core_product_id']
            product_vals["related_customer_id"]= kwargs['related_customer_id']
        except Exception as e:
            return {"error": e}

        product_ids = request.env['product.product'].sudo().search([('id', '=', id)])

        for product_id in product_ids:
            product_id.write(product_vals)
  
        for product_id in product_ids:
            data = {
                "id": product_id.id,
                "name": product_id.name,
                "price": product_id.list_price,
                "cost": product_id.standard_price,
                "related_customer_id": product_id.partner_id.carrier_carrier_id,
                "related_customer_name": product_id.partner_id.name,
                "core_product_id": product_id.core_product_id
                }
            products_list.append(data)

        response = {"data": products_list, "message": "Product(s) found"}
        return response
    
    @http.route('/api/products', type='json', auth='api_key', website=False, methods=['POST'])
    def create(self, **kwargs):
        '''Create a product and return product ID'''
        product_ids = request.env['product.product'].sudo().search([('core_product_id', '=', kwargs["core_product_id"])])

        partner_id = request.env['res.partner'].sudo().search([('core_shipper_id', '=',kwargs['shipper_id'])])

        if product_ids is not None:
            for product_id in product_ids:
                data = {
                    "id": product_id.id, 
                    "name": product_id.name, 
                    "price": product_id.list_price,
                    "cost": product_id.standard_price,
                    "related_customer_id": product_id.partner_id.carrier_carrier_id,
                    "core_product_id": product_id.core_product_id, 
                    "message": "product already exists"}
                return data

        vals = {
            "name": kwargs['name'],
            "list_price": kwargs['price'],
            "standard_price": kwargs['cost'],
            "partner_id": partner_id.id,
            "default_code": kwargs["default_code"],
            "core_product_id": kwargs['core_product_id']
            }

        new_product = request.env['product.product'].create(vals)

        data = {
            "id": new_product.id,
            "name": new_product.name,
            "price": new_product.list_price,
            "cost": new_product.standard_price,
            "shipper_id": new_product.partner_id.core_shipper_id,
            "core_product_id": new_product.core_product_id, 
            "message": "Product successfully created"}
        return data


class Partner(http.Controller):
    '''Handle partners'''

    @http.route('/api/shippers', type='json', auth='api_key', website=False, methods=['GET'])
    def get_shippers(self):
        '''Return all shippers'''
        partners_list = []

        partner_ids = request.env['res.partner'].sudo().search([('is_customer','=',True)])

        for partner_id in partner_ids:
            data = {
                "id": partner_id.id, 
                "name": partner_id.name,
                "phone": partner_id.phone,
                "email": partner_id.email,
                "carrier_id": partner_id.carrier_carrier_id,
                "shipper_id": partner_id.core_shipper_id,
                "is_vendor": partner_id.is_vendor,
                "is_customer": partner_id.is_customer,
                "is_partner_vatable": partner_id.is_partner_vatable
                }
            partners_list.append(data)

        response = {"data": partners_list, "message": "Partners(s) found"}
        return response

    @http.route('/api/partners', type='json', auth='api_key', website=False, methods=['GET'])
    def get_partners(self):
        '''Return all partners'''
        partners_list = []

        partner_ids = request.env['res.partner'].sudo().search([('is_vendor','=',True)])

        for partner_id in partner_ids:
            data = {
                "id": partner_id.id, 
                "name": partner_id.name,
                "phone": partner_id.phone,
                "email": partner_id.email,
                "carrier_id": partner_id.carrier_carrier_id,
                "shipper_id": partner_id.core_shipper_id,
                "is_vendor": partner_id.is_vendor,
                "is_customer": partner_id.is_customer,
                "is_partner_vatable": partner_id.is_partner_vatable
                }
            partners_list.append(data)

        response = {"data": partners_list, "message": "Partners(s) found"}
        return response

    @http.route('/api/partners/<int:carrier_id>', type='json', auth='api_key', website=False, methods=['GET'])
    def get_partner(self, carrier_id=None, **kwargs):
        '''Return a single partner's information'''
        partners_list = []

        partner_ids = request.env['res.partner'].sudo().search([('carrier_carrier_id', '=', carrier_id)])

        for partner_id in partner_ids:
            data = {
                "id": partner_id.id, 
                "name": partner_id.name,
                "phone": partner_id.phone,
                "email": partner_id.email,
                "carrier_id": partner_id.carrier_carrier_id,
                "shipper_id": partner_id.core_shipper_id,
                "is_vendor": partner_id.is_vendor,
                "is_customer": partner_id.is_customer,
                "is_partner_vatable": partner_id.is_partner_vatable
                }
            partners_list.append(data)

        response = {"data": partners_list, "message": "Partners(s) found"}
        return response
    
    @http.route('/api/shippers/<int:shipper_id>', type='json', auth='api_key', website=False, methods=['GET'])
    def get_shipper(self, shipper_id=None, **kwargs):
        '''Return a single shipper information'''
        partners_list = []

        partner_ids = request.env['res.partner'].sudo().search([('core_shipper_id', '=', shipper_id)])

        for partner_id in partner_ids:
            data = {
                "id": partner_id.id, 
                "name": partner_id.name,
                "phone": partner_id.phone,
                "email": partner_id.email,
                "carrier_id": partner_id.carrier_carrier_id,
                "shipper_id": partner_id.core_shipper_id,
                "is_vendor": partner_id.is_vendor,
                "is_customer": partner_id.is_customer,
                "is_partner_vatable": partner_id.is_partner_vatable
                }
            partners_list.append(data)

        response = {"data": partners_list, "message": "Partners(s) found"}
        return response
    
    @http.route('/api/partners/<int:shipper_id>', type='json', auth='api_key', website=False, methods=['PATCH'])
    def edit_shippers(self, shipper_id=None, **kwargs):
        '''Edit shippers'''
        partner_ids = request.env['res.partner'].sudo().search([('core_shipper_id', '=', shipper_id)])
        vals = {
                "name" : kwargs["partner"],
                "phone" : kwargs['phone'],
                'email': kwargs["email"],
                "carrier_carrier_id": kwargs["carrier_id"],
                "is_vendor": kwargs["is_vendor"],
                "is_customer": kwargs["is_customer"],
                "is_partner_vatable": kwargs["is_partner_vatable"],
                "core_shipper_id": kwargs["shipper_id"]
            }

        for partner_id in partner_ids:
            partner_id.update(vals)

        return {"data": partner_id.name, "message": "Partner successfully updated."}


    @http.route('/api/partners/<int:carrier_id>', type='json', auth='api_key', website=False, methods=['PATCH'])
    def edit_partners(self, carrier_id=None, **kwargs):
        '''Edit partners'''
        partner_ids = request.env['res.partner'].sudo().search([('carrier_carrier_id', '=', carrier_id)])
        vals = {
                "name" : kwargs["partner"],
                "phone" : kwargs['phone'],
                'email': kwargs["email"],
                "carrier_carrier_id": kwargs["carrier_id"],
                "is_vendor": kwargs["is_vendor"],
                "is_customer": kwargs["is_customer"],
                "is_partner_vatable": kwargs["is_partner_vatable"],
                "core_shipper_id": kwargs["shipper_id"]
            }

        for partner_id in partner_ids:
            partner_id.update(vals)

        return {"data": partner_id.name, "message": "Partner successfully updated."}

    
    @http.route('/api/partners', type='json', auth='api_key', website=False, methods=['POST'])
    def create_partners(self, **kwargs):
        '''Create partners if they dont exist and return partner id'''

        partners_list = []

        partner_ids = request.env['res.partner'].sudo().search([('carrier_carrier_id', '=', kwargs["carrier_id"])])
        
        
        if partner_ids:
            for partner_id in partner_ids:
                data = {"id": partner_id.id, "name": partner_id.name}
                partners_list.append(data)

            response = {"data": partners_list, "message": "Partner already exists!"}

            return response
        
        else:
            vals = {
                "name" : kwargs["partner"],
                "phone" : kwargs['phone'],
                'email': kwargs["email"],
                "carrier_carrier_id": kwargs["carrier_id"],
                "is_vendor": kwargs["is_vendor"],
                "is_customer": kwargs["is_customer"],
                "is_partner_vatable": kwargs["is_partner_vatable"],
                "core_shipper_id": kwargs["shipper_id"]
            }

            partner_id = request.env['res.partner'].create(vals)

            data = {
                "id": partner_id.id, 
                "name": partner_id.name,
                "phone": partner_id.phone,
                "email": partner_id.email,
                "carrier_id": partner_id.carrier_carrier_id,
                "shipper_id": partner_id.core_shipper_id,
                "is_vendor": partner_id.is_vendor,
                "is_customer": partner_id.is_customer,
                "is_partner_vatable": partner_id.is_partner_vatable
                }
            partners_list.append(data)

        response = {"data": partners_list, "message": "Partner created successfully!"}
        return response

    @http.route('/api/shippers', type='json', auth='api_key', website=False, methods=['POST'])
    def create_shippers(self, **kwargs):
        '''Create partners if they dont exist and return partner id'''

        partners_list = []
        partner_ids = request.env['res.partner'].sudo().search([('core_shipper_id', '=', kwargs["shipper_id"])])
        
        if partner_ids:
            for partner_id in partner_ids:
                data = {"id": partner_id.id, "name": partner_id.name}
                partners_list.append(data)

            response = {"data": partners_list, "message": "Partner already exists!"}

            return response
        
        else:
            vals = {
                "name" : kwargs["partner"],
                "phone" : kwargs['phone'],
                'email': kwargs["email"],
                "carrier_carrier_id": kwargs["carrier_id"],
                "is_vendor": kwargs["is_vendor"],
                "is_customer": kwargs["is_customer"],
                "is_partner_vatable": kwargs["is_partner_vatable"],
                "core_shipper_id": kwargs["shipper_id"],
                "is_vendor":False,
                "is_customer": True
            }

            partner_id = request.env['res.partner'].create(vals)

            data = {
                "id": partner_id.id, 
                "name": partner_id.name,
                "phone": partner_id.phone,
                "email": partner_id.email,
                "carrier_id": partner_id.carrier_carrier_id,
                "shipper_id": partner_id.core_shipper_id,
                "is_vendor": partner_id.is_vendor,
                "is_customer": partner_id.is_customer,
                "is_partner_vatable": partner_id.is_partner_vatable
                }
            partners_list.append(data)

        response = {"data": partners_list, "message": "Shipper created successfully!"}
        return response


class Invoices(http.Controller):
    '''Handle Invoices '''

    @http.route('/api/invoices/<int:partner_id>/draft', type='json', auth='api_key', website=False, methods=['GET'])
    def get_draft_invoices(self, **kwargs):
        '''Retrieve all draft invoices for a particular partner'''
        partner_id = kwargs['partner_id']
        domain = [('partner_id', '=', partner_id), ('move_type', '=', 'out_invoice'), ('state', '=', 'draft')]

        draft_invoices = request.env['account.move'].sudo().search_read(domain)
        response = {"data": draft_invoices, "message": "Invoice(s)"}
        return response

    @http.route('/api/invoices/<int:partner_id>/posted', type='json', auth='api_key', website=False, methods=['GET'])
    def get_posted_invoices(self, **kwargs):
        '''Retrieve all posted invoices for a particular partner'''
        partner_id = kwargs['partner_id']

        domain = [('partner_id', '=', partner_id), ('move_type', '=', 'out_invoice'), ('state', '=', 'posted')]

        posted_invoices = request.env['account.move'].sudo().search_read(domain)
        response = {"data": posted_invoices, "message": "Invoice(s)"}
        return response
    
    @http.route('/api/invoices/<int:partner_id>/paid', type='json', auth='api_key', website=False, methods=['GET'])
    def get_paid_invoices(self, **kwargs):
        '''Retrieve all paid invoices for a particular partner'''
        partner_id = kwargs['partner_id']

        domain = [('partner_id', '=', partner_id), ('move_type', '=', 'out_invoice'), ('state', '=', 'paid')]

        paid_invoices = request.env['account.move'].sudo().search_read(domain)
        response = {"data": paid_invoices, "message": "Invoice(s)"}
        return response
    
    @http.route('/api/invoices/<int:partner_id>', type='json', auth='api_key', website=False, methods=['GET'])
    def get_invoices(self, **kwargs):
        '''Retrieve all invoices for a particular partner'''

        partner_id = kwargs['partner_id']

        domain = [('partner_id', '=', partner_id), ('move_type', '=', 'out_invoice')]
        invoices = request.env['account.move'].sudo().search_read(domain)
        response = {"data": invoices, "message": "Invoice(s)"}
        return response
    
    @http.route('/api/invoice/<int:order_id>', type='json', auth='api_key', website=False, methods=['GET'])
    def get_specific_invoices(self, **kwargs):
        '''Retrieve all invoices for a particular partner'''

        id = kwargs['order_id']

        domain = [('id', '=', id), ('move_type', '=', 'out_invoice')]

        specific_invoice = request.env['account.move'].sudo().search_read(domain)
        response = {"data": specific_invoice, "message": "Invoice(s)"}
        return response