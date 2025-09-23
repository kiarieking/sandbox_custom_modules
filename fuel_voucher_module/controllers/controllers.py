# -*- coding: utf-8 -*-
# from odoo import http


# class FuelVoucherModule(http.Controller):
#     @http.route('/fuel_voucher_module/fuel_voucher_module/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fuel_voucher_module/fuel_voucher_module/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fuel_voucher_module.listing', {
#             'root': '/fuel_voucher_module/fuel_voucher_module',
#             'objects': http.request.env['fuel_voucher_module.fuel_voucher_module'].search([]),
#         })

#     @http.route('/fuel_voucher_module/fuel_voucher_module/objects/<model("fuel_voucher_module.fuel_voucher_module"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fuel_voucher_module.object', {
#             'object': obj
#         })
