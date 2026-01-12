# -*- coding: utf-8 -*-
# from odoo import http


# class QuatrixBillingModule(http.Controller):
#     @http.route('/quatrix_billing_module/quatrix_billing_module/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/quatrix_billing_module/quatrix_billing_module/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('quatrix_billing_module.listing', {
#             'root': '/quatrix_billing_module/quatrix_billing_module',
#             'objects': http.request.env['quatrix_billing_module.quatrix_billing_module'].search([]),
#         })

#     @http.route('/quatrix_billing_module/quatrix_billing_module/objects/<model("quatrix_billing_module.quatrix_billing_module"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('quatrix_billing_module.object', {
#             'object': obj
#         })
