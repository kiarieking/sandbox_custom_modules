# -*- coding: utf-8 -*-
# from odoo import http


# class QuatrixCarrierOrders(http.Controller):
#     @http.route('/quatrix_carrier_orders/quatrix_carrier_orders/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/quatrix_carrier_orders/quatrix_carrier_orders/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('quatrix_carrier_orders.listing', {
#             'root': '/quatrix_carrier_orders/quatrix_carrier_orders',
#             'objects': http.request.env['quatrix_carrier_orders.quatrix_carrier_orders'].search([]),
#         })

#     @http.route('/quatrix_carrier_orders/quatrix_carrier_orders/objects/<model("quatrix_carrier_orders.quatrix_carrier_orders"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('quatrix_carrier_orders.object', {
#             'object': obj
#         })
