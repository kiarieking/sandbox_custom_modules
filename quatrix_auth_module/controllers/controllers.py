# -*- coding: utf-8 -*-
# from odoo import http


# class QuatrixAuthModule(http.Controller):
#     @http.route('/quatrix_auth_module/quatrix_auth_module/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/quatrix_auth_module/quatrix_auth_module/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('quatrix_auth_module.listing', {
#             'root': '/quatrix_auth_module/quatrix_auth_module',
#             'objects': http.request.env['quatrix_auth_module.quatrix_auth_module'].search([]),
#         })

#     @http.route('/quatrix_auth_module/quatrix_auth_module/objects/<model("quatrix_auth_module.quatrix_auth_module"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('quatrix_auth_module.object', {
#             'object': obj
#         })
