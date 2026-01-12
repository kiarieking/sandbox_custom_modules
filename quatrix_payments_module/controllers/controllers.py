# -*- coding: utf-8 -*-
# from odoo import http


# class QuatrixPaymentsModule(http.Controller):
#     @http.route('/quatrix_payments_module/quatrix_payments_module/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/quatrix_payments_module/quatrix_payments_module/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('quatrix_payments_module.listing', {
#             'root': '/quatrix_payments_module/quatrix_payments_module',
#             'objects': http.request.env['quatrix_payments_module.quatrix_payments_module'].search([]),
#         })

#     @http.route('/quatrix_payments_module/quatrix_payments_module/objects/<model("quatrix_payments_module.quatrix_payments_module"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('quatrix_payments_module.object', {
#             'object': obj
#         })
