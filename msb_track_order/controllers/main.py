# -*- coding: utf-8 -*-
# Copyright 2021 Max Services Biz. All rights reserved.
import pdb
import re
from odoo import fields
from odoo.http import Controller, request, route


class MBTrackOrder(Controller):

    @route(['/track-order'], type='http', auth="public", website=True , methods=['POST', 'GET'], csrf=True)
    def track_order(self, **kw):        
        vals = {
            'items': [],
            'so_name': kw.get("so-name", None),
            'so_id': None,
            'estimated_delivery_date': None,
            'carrier_code': None,
            'carrier_name': None,
            'message':None
        }
        if request.httprequest.method == "POST":
            to_date = lambda so, dt, sz=19: str(fields.Datetime.context_timestamp(so, fields.Datetime.from_string(dt)))[:sz]
            if vals.get('so_name'):
                so = request.env['sale.order'].sudo().search(
                    [('name','=',vals.get('so_name'))]
                )            
                if len(so):
                    if hasattr(so, 'commitment_date'):
                        vals.update({'estimated_delivery_date': to_date(so, so.commitment_date, 10)})

                    if hasattr(so, 'picking_ids'):
                        carrier_code =""
                        carrier_name =""
                        for picking in  so.picking_ids:
                            if hasattr(picking, 'carrier_id') and picking.carrier_id:
                                carrier_name += picking.carrier_id.name + ", "
                            if hasattr( picking, 'carrier_tracking_ref') and  picking.carrier_tracking_ref:
                                carrier_code += picking.carrier_tracking_ref+ ", "
                        vals.update({
                            'carrier_code': carrier_code[:-2],
                            'carrier_name': carrier_name[:-2],
                        })
                    items = []
                    for message in so.message_ids:
                        name = re.search(r't-name(.*)t-name', message.body)
                        if not name:
                            continue
                        name = str(name.group()).replace('t-name','').strip()

                        description = re.search(r't-desc(.*)t-desc', message.body)
                        if description:
                            description = str(description.group()).replace('t-desc','').strip()
                        else:
                            description = ''
                        items.append(
                            {
                                'date': to_date(so, message.date),
                                'name': name,
                                'description': description
                            }
                        )
                    vals.update({'items':items})
                    vals.update({'so_id': so.id})                
                else:
                    vals.update({'message': "La orden #%s no fue encontrada." % vals.get('so_name')})
            else:
                vals.update({'message': "El Número de orden es requerido"})
        
        return request.render("msb_track_order.msb_track_order_templ", vals)