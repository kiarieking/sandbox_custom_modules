# -*- coding: utf-8 -*-
from odoo import http
from datetime import datetime
from odoo.http import Response, request

class Dispatch(http.Controller):

    @http.route('/api/dispatch', type="json", auth='api_key', website=False, methods=['GET'])
    def get_records(self, **kwargs):
  
        dispatch_records = request.env['quatrix.dispatch'].search([])

        orders = []
        if not dispatch_records:
            Response.status='400'
        for record in dispatch_records:
            dispatch_record = request.env['quatrix.dispatch'].search_read([('id','=', record.id)])

            if dispatch_record:
                for record in dispatch_records:
                    vals = {}
                    vals['shipper_id'] = record.partner_id.core_shipper_id
                    vals['shipper_name'] = record.partner_id.name
                    vals['vehicle_registration'] = record.vehicle_id.license_plate
                    vals['dispatch_number'] = record.name
                    vals['date_dispatch'] = record.date_dispatch
                    vals['date_delivery'] = record.date_delivery
                    vals['pod_link'] = record.pod_link
                    vals['status'] = record.status
                    vals['sale_document_number'] = record.sale_doc
                    vals['invoice_document_number'] = record.inv_doc

                    line = {}

                    for order_line in record.order_ids:
                        line["product_id"] = order_line.product_id.core_product_id
                        line["product_name"] = order_line.product_id.name
                        line["order_number"] = order_line.order_no
                        line["description"] = order_line.description
                        line["quantity"] = order_line.quantity
                        line["carrier_charges"] = order_line.carrier_price
                        line["unit_price"] = order_line.price_unit
                        line["trip_cost"] = order_line.price_unit * order_line.quantity

                    vals['lines'] = line
            orders.append(vals)
        data = {'status': 200, 'data': orders, 'message': 'Dispatch Record(s)'}
        return data


    @http.route('/api/dispatch/<int:order_id>', type="json", auth='api_key', website=False, methods=['GET'])
    def get_single_record(self, order_id=None, **kwargs):
  
        domain=[('id','=', order_id)]
        dispatch_records = request.env['quatrix.dispatch'].search(domain)

        orders = []
        if not dispatch_records:
            Response.status='400'
        for record in dispatch_records:
            vals = {}
            vals['shipper_id'] = record.partner_id.core_shipper_id
            vals['shipper_name'] = record.partner_id.name
            vals['vehicle_registration'] = record.vehicle_id.license_plate
            vals['dispatch_number'] = record.name
            vals['date_dispatch'] = record.date_dispatch
            vals['date_delivery'] = record.date_delivery
            vals['pod_link'] = record.pod_link
            vals['status'] = record.status
            vals['sale_document_number'] = record.sale_doc
            vals['invoice_document_number'] = record.inv_doc

            line = {}

            for order_line in record.order_ids:
                line["product_id"] = order_line.product_id.core_product_id
                line["product_name"] = order_line.product_id.name
                line["order_number"] = order_line.order_no
                line["description"] = order_line.description
                line["quantity"] = order_line.quantity
                line["carrier_charges"] = order_line.carrier_price
                line["unit_price"] = order_line.price_unit
                line["trip_cost"] = order_line.price_unit * order_line.quantity

            vals['lines'] = line
            orders.append(vals)
        data = {'status': 200, 'data': orders, 'message': 'Dispatch Record(s)'}
        return data
    
    @http.route('/api/dispatch/order/<string:order_no>', type="json", auth='api_key', website=False, methods=['GET'])
    def get_single_record_by_order_no(self, order_no=None, **kwargs):
  
        domain=[('order_no','=', order_no)]
        dispatch_line_ids = request.env['quatrix.dispatch.line'].search(domain)

        order_id = None

        for dispatch_line_id in dispatch_line_ids:
            order_id = dispatch_line_id.order_id

        dispatch_records = request.env['quatrix.dispatch'].search([('id', '=', order_id.id)])

        orders = []
        if not dispatch_records:
            Response.status='400'
        for record in dispatch_records:
            vals = {}
            vals['shipper_id'] = record.partner_id.core_shipper_id
            vals['shipper_name'] = record.partner_id.name
            vals['vehicle_registration'] = record.vehicle_id.license_plate
            vals['dispatch_number'] = record.name
            vals['date_dispatch'] = record.date_dispatch
            vals['date_delivery'] = record.date_delivery
            vals['pod_link'] = record.pod_link
            vals['status'] = record.status
            vals['sale_document_number'] = record.sale_doc
            vals['invoice_document_number'] = record.inv_doc

            line = {}

            for order_line in record.order_ids:
                line["product_id"] = order_line.product_id.core_product_id
                line["product_name"] = order_line.product_id.name
                line["order_number"] = order_line.order_no
                line["description"] = order_line.description
                line["quantity"] = order_line.quantity
                line["carrier_charges"] = order_line.carrier_price
                line["unit_price"] = order_line.price_unit
                line["trip_cost"] = order_line.price_unit * order_line.quantity

            vals['lines'] = line
            orders.append(vals)
        data = {'status': 200, 'data': orders, 'message': 'Dispatch Record(s)'}
        return data

    @http.route('/api/dispatch', type="json", auth='api_key', website=False, methods=['POST'])
    def create_record(self, **kwargs):

        order_lines = []
        order_numbers = []

        product = None

        partner = request.env['res.partner'].search([('core_shipper_id', '=', kwargs["shipper_id"])])
        vehicle = request.env['fleet.vehicle'].search([('carrier_vehicle_id', '=', kwargs["vehicle_id"])])

        if not partner or not vehicle:
            return {"status":400,"error":"shipper or vehicle does not exist."}

        vals = {
            "partner_id": partner.id,
            "vehicle_id": vehicle.id,
            "date_dispatch": datetime.strptime(kwargs["date_dispatch"], '%Y-%m-%d %H:%M:%S.%f'),
            "date_delivery": datetime.strptime(kwargs["date_delivery"], '%Y-%m-%d %H:%M:%S.%f'),
        }
        
        lines = kwargs["order_line"]
        
        for line in lines:
            product_ids = request.env['product.product'].sudo().search([('core_product_id', '=', line["core_product_id"])])

            order_exists = request.env["quatrix.dispatch.line"].search([('order_no', '=', line["order_no"])])

            if order_exists:
                response = {'status': 400, "error": "dispatch failed! Order Exists"}
                return response
            
            for product_id in product_ids: product = product_id

            line_vals = [(0,0,{
                "product_id": product.id,
                "order_no": line["order_no"],
                "quantity":line["quantity"],
                "description": line["description"],
                "price_unit": product.list_price,
                "carrier_price": product.standard_price * float(line["quantity"])
            })]

            order_lines.append(line_vals)
            order_numbers.append(line['order_no'])
        
        vals["order_ids"] = order_lines[0]

        try:
            new_dispatch = request.env["quatrix.dispatch"].create(vals)
            response = {'status': 201, "message": "Success!", "dispatch_id": new_dispatch.id}
            return response

        except Exception as e:
            response = {'status': 400, "error": ("dispatch failed! " + str(e))}
            return response


    @http.route('/api/dispatch/<int:order_id>', type="json", auth='api_key', website=False, methods=['PATCH'])
    def edit_record(self, **kwargs):
        order_id = kwargs['order_id']
        record = request.env['quatrix.dispatch'].sudo().search([('id','=',order_id)])
        vehicle_id = None

        if kwargs["license_plate"]:
            vehicle_id = request.env['fleet.vehicle'].sudo().search([('license_plate', '=', kwargs["license_plate"])])

        if vehicle_id is not None:
            form_vals = {'vehicle_id': vehicle_id.id}
            record.write(form_vals)

        order_number = None

        items = kwargs['lines']
        for item in items:
            order_number = item["order_no"]
            for line in record.order_ids:
                if line.order_no != order_number:
                    return
                line.write(item)

        data = {'status': 200, 'data': kwargs, 'response': record.name, 'message': 'Dispatch record updated!'}
        return data

    @http.route('/api/dispatch/<int:order_id>/pod', type="json", auth='api_key', website=False, methods=['PATCH'])
    def update_pod(self, **kwargs):
        order_id = kwargs['order_id']
        record = request.env['quatrix.dispatch'].sudo().search([('id','=',order_id)])

        vals = {"pod_link": kwargs["pod_link"]}
        record.write(vals)

        data = {'status': 200, 'response': record.name, 'message': 'POD successfully updated!'}

        return data



    ############# VEHICLES
    
    # Get single vehicle model
    @http.route('/api/vehicles/models/<string:model>', type="json", auth='api_key', website=False, methods=['GET'])
    def get_vehicle_model(self, model=None, **kwargs):
        # model = kwargs['model']

        # Check if carrier exists
        record = request.env['fleet.vehicle.model'].sudo().search([('name','=',model)])
        if record:
           data = {'status': 200, 'message': 'ok', "error": None}
           return data

        data = {'status': 400, 'error': 'model does not exist.', "message": None}
        return data

    # Add vehicle models
    @http.route('/api/vehicles/models', type="json", auth='api_key', website=False, methods=['POST'])
    def add_model(self, **kwargs):
        model = kwargs['model']
        manufacturer = kwargs['manufacturer']

        vals = {"model": kwargs["model"], "manufacturer": kwargs["manufacturer"]}
        model_id = request.env['fleet.vehicle.model'].sudo().search([('name','=',model)])
        if model_id:
            data = {"status": 400, "error": "model already exists", "message":None}
            return data

        brand_id = request.env['fleet.vehicle.model.brand'].sudo().search([('name','=',manufacturer)])
        if brand_id:
            vals = {"name": model, brand_id: brand_id.id}
            new_record = request.env['fleet.vehicle.model'].sudo().create(vals)
            data = {'status': 201,'message': 'model added successfully!', "error": None}

            return data
        else:
            vals = {"name": manufacturer}
            brand_id = request.env['fleet.vehicle.model'].sudo().create(vals)

            new_record = request.env['fleet.vehicle.model'].sudo().create(vals)
            data = {'status': 201, 'message': 'Model %s added successfully!'%(new_record.name), "error": None}

            return data
    
    # Get single vehicle
    @http.route('/api/vehicles/<int:core_vehicle_id>', type="json", auth='api_key', website=False, methods=['GET'])
    def get_vehicle(self, core_vehicle_id=None, **kwargs):
        # Check if vehicle exists
        record = request.env['fleet.vehicle'].sudo().search([('carrier_vehicle_id','=',core_vehicle_id)])
        if not record:
            data = {'status': 400, 'error': 'Vehicle does not exist.'}
            return data
            
        response = {
            "model": record.model_id.name,
            "carrier_id": record.carrier_carrier_id,
            "carrier_name": record.carrier_id.name,
            "driver_id": record.carrier_driver_id,
            "driver_name": record.driver_id.name,
            "vehicle_id": record.carrier_vehicle_id,
            "license_plate": record.license_plate,
            "vehicle_size": record.vehicle_size
            }

        data = {'status': 200, 'response': response, "error": None}

        return data

    @http.route('/api/vehicles', type="json", auth='api_key', website=False, methods=['POST'])
    def add_vehicle(self, **kwargs):
        model = kwargs['model']
        license_plate = kwargs['license_plate']
        vehicle_id = kwargs['vehicle_id']
        carrier_id = kwargs['carrier_id']
        driver_id = kwargs['driver_id']
        vehicle_size = kwargs["vehicle_size"] # Vehicle Size 14T

        # Check if vehicle already exists
        record = request.env['fleet.vehicle'].sudo().search([('license_plate','=',license_plate)])
        if record:
            data = {"status": 400, "error": "Vehicle already exists", "message": None}
            return data
        
        # Check if carrier exists
        carrier = request.env['res.partner'].sudo().search([('carrier_carrier_id','=',carrier_id)])
        if not carrier:
            data = {"status": 400, "error": "Carrier does not exist.", "message": None}
            return data
        
        driver = request.env['res.partner'].sudo().search([('carrier_carrier_id','=',driver_id)])
        if not driver:
            data = {"status": 400, "error": "Driver does not exist.", "message": None}
            return data
        
        # Get model ID
        model_id = request.env['fleet.vehicle.model'].sudo().search([('name','=',model)])
        if not model_id:
            data = {"status": 400, "error": "Model does not exist.", "message": None}
            return data

        vals = {
            "model_id": model_id.id,
            "carrier_carrier_id": carrier_id,
            "carrier_driver_id": driver_id,
            "carrier_vehicle_id": str(vehicle_id),
            "license_plate": license_plate,
            "vehicle_size": vehicle_size
            }

        record = request.env['fleet.vehicle'].sudo().create(vals)

        res = {
            "model": record.model_id.name,
            "carrier_id": record.carrier_carrier_id,
            "carrier_name": record.carrier_id.name,
            "driver_id": record.carrier_driver_id,
            "driver_name": record.driver_id.name,
            "vehicle_id": record.carrier_vehicle_id,
            "license_plate": record.license_plate,
            "vehicle_size": record.vehicle_size
        }

        data = {'status': 201, 'response': res, 'message': 'Vehicle added Successfully!', "error": None}
        return data
    

    @http.route('/api/vehicles/<int:vehicle_id>', type="json", auth='api_key', website=False, methods=['PATCH'])
    def edit_vehicle(self, vehicle_id=None, **kwargs):

        model = kwargs['model']
        license_plate = kwargs['license_plate']
        carrier_id = kwargs['carrier_id']
        vehicle_size = kwargs["vehicle_size"]
        driver_id = kwargs["driver_id"]

        # Check if vehicle already exists
        record = request.env['fleet.vehicle'].sudo().search([('carrier_vehicle_id','=',vehicle_id)])
        if not record:
            data = {"status": 400, "error": "Vehicle does not exist"}
            return data
        
        # Check if carrier exists
        carrier = request.env['res.partner'].sudo().search([('carrier_carrier_id','=',carrier_id)])
        if not carrier:
            data = {"status": 400, "error": "Carrier does not exist.", "message": None}
            return data
        
        driver = request.env['res.partner'].sudo().search([('carrier_carrier_id','=',driver_id)])
        if not driver:
            data = {"status": 400, "error": "Driver does not exist.", "message": None}
            return data
        
        # Get model ID
        model_id = request.env['fleet.vehicle.model'].sudo().search([('name','=',model)])
        if not model_id:
            data = {"status": 400, "error": "Model does not exist.", "message": None}
            return data

        vals = {
            "model_id": model_id.id,
            "carrier_carrier_id": carrier_id,
            "vehicle_size": vehicle_size,
            "carrier_driver_id": driver_id
            }

        response = None

        try:
            record.update(vals)
            response = {
                "model": record.model_id.name,
                "carrier_id": record.carrier_carrier_id,
                "carrier_name": record.carrier_id.name,
                "driver_id": record.carrier_driver_id,
                "driver_name": record.driver_id.name,
                "vehicle_id": record.carrier_vehicle_id,
                "license_plate": record.license_plate,
                "vehicle_size": record.vehicle_size
            }

        except:
            for rec in record:
                rec.update(vals)

                response = {
                    "model": rec.model_id.name,
                    "carrier_id": rec.carrier_carrier_id,
                    "carrier_name": rec.carrier_id.name,
                     "driver_id": record.carrier_driver_id,
                    "driver_name": record.driver_id.name,
                    "vehicle_id": rec.carrier_vehicle_id,
                    "license_plate": rec.license_plate,
                    "vehicle_size": rec.vehicle_size
                }

        data = {'status': 200, 'response': response, 'message': 'Vehicle updated successfully!', "error": None}
        return data




   ###### CARRIERS

    # Get single carrier
    # @http.route('/api/carriers', type="json", auth='api_key', website=False, methods=['GET'])
    # def get_carrier(self, **kwargs):
    #     carrier_id = kwargs['carrier_id']

    #     # Check if carrier exists
    #     record = request.env['res.partner'].sudo().search([('carrier_carrier_id','=',carrier_id)])
    #     if record:
    #        data = {'status': 200, 'message': 'ok', "error": None}
    #        return data

    #     data = {'status': 400, 'error': 'User does not exist.'}
    #     return data

    # # Add carriers
    # @http.route('/api/carriers', type="json", auth='api_key', website=False, methods=['POST'])
    # def add_carrier(self, **kwargs):
    #     carrier_id = kwargs['carrier_id']
    #     carrier_name = kwargs['carrier_name']

    #     # Check if carrier exists
    #     record = request.env['res.partner'].sudo().search([('carrier_carrier_id','=',carrier_id)])
    #     if record:
    #         data = {"status": 400, "error": record.name + " already exists", "message": None}
    #         return data
    #     vals = {"carrier_carrier_id": carrier_id, "name": carrier_name}
    #     new_record = request.env['res.partner'].sudo().create(vals)

    #     data = {'status': 201, 'message': 'carrier added successfully!', "error": None}

    #     return data