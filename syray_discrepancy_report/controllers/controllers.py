# -*- coding: utf-8 -*-
from odoo import http

# class SyraySoDoDate(http.Controller):
#     @http.route('/syray_so_do_date/syray_so_do_date/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/syray_so_do_date/syray_so_do_date/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('syray_so_do_date.listing', {
#             'root': '/syray_so_do_date/syray_so_do_date',
#             'objects': http.request.env['syray_so_do_date.syray_so_do_date'].search([]),
#         })

#     @http.route('/syray_so_do_date/syray_so_do_date/objects/<model("syray_so_do_date.syray_so_do_date"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('syray_so_do_date.object', {
#             'object': obj
#         })