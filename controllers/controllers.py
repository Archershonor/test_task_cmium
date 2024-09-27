# -*- coding: utf-8 -*-
from odoo import http, fields
from odoo.http import request
import json
from datetime import datetime


class TestTasks(http.Controller):
    @http.route('/test_tasks/courier', type='http', methods=['GET'], auth='public')
    def courier_info(self, **kw):
        try:
            courier_id = kw.get('courier_id')
            date_str = kw.get('date')
            if date_str:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
            else:
                date = datetime.today()

            day_start = date.strftime('%Y-%m-%d 00:00:00')
            day_end = date.strftime('%Y-%m-%d 23:59:59')
            orders_domain = [('delivery_partner_id', '=', int(courier_id)),
                             ('date_order', '>=', day_start),
                             ('date_order', '<=', day_end)]
            courier_info = http.request.env['res.partner'].sudo().search([('id', '=', int(courier_id))], limit=1)
            orders = http.request.env['sale.order'].sudo().search(orders_domain)

            orders_list = []
            for order in orders:
                orders_list.append(
                    {
                        'order_id': order.id,
                        'order_number': order.name,
                        'client_name': order.partner_id.name,
                        'client_phone': order.partner_id.phone,
                        'delivery_address': order.partner_id.contact_address,
                        # TODO: where is delivery state?
                        'delivery_status': 'Delivered' if order.commitment_date else 'Awaiting delivery'
                    }
                )
            response_data = {
                'courier_info':
                    {
                        'courier_id': courier_info.id,
                        'name': courier_info.name,
                        'phone': courier_info.phone,
                        'email': courier_info.email
                    },
                'orders': orders_list
            }

            return request.make_response(
                json.dumps(response_data),
                headers=[('Content-Type', 'application/json')],
                status=200)

        except Exception as e:
            return request.make_response(
                json.dumps({'error': 'An unexpected error occurred: {}'.format(str(e))}),
                headers=[('Content-Type', 'application/json')],
                status=500
            )


#     @http.route('/test_tasks/test_tasks/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('test_tasks.listing', {
#             'root': '/test_tasks/test_tasks',
#             'objects': http.request.env['test_tasks.test_tasks'].search([]),
#         })

#     @http.route('/test_tasks/test_tasks/objects/<model("test_tasks.test_tasks"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('test_tasks.object', {
#             'object': obj
#         })
