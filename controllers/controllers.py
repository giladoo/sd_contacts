# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.modules.module import get_module_resource
# from odoo.addons.http_routing.models.ir_http import url_for
from odoo.tools import ustr
from datetime import datetime, timedelta
# import datetime
import jdatetime
from werkzeug.wrappers import Response

from icecream import ic
import logging
import json
import base64


logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG)
logger = logging.getLogger(__name__)



# #######################################################################################
class SdContactsController(http.Controller):

    # #######################################################################################
    @http.route('/employee/contacts/', type='http', auth="public", website=True)
    def sd_employee_phone_list(self, **kwargs):
        # ic('sd_employee_phone_list')
        return http.request.render('sd_contacts.employee_contacts', { })


    @http.route('/employee/contactdata', type='json', auth="public", website=True)
    def sd_employee_contact_data(self, **kwargs):
        return request.env['hr.employee'].sudo().contact_web()









    class ContactController(http.Controller):
        @http.route('/contacts', type='http', auth='public', website=True)
        def list_contacts(self):
            return request.render('sd_contacts.contact_template')

    @http.route('/contacts/search', type='json', auth='public', website=True)
    def search_contacts(self, search_name=None, search_phone=None):
        domain = []
        if search_name:
            domain.append(('name', 'ilike', search_name))
        if search_phone:
            domain.append(('phone', 'ilike', search_phone))
        contacts = request.env['res.partner'].search_read(domain, ['name', 'phone'])
        return json.dumps(contacts)




    @http.route('/employee/contactsimage/<int:employee_id>', type='http', auth='public', website=True)
    def get_employee_avatar(self, employee_id, **kw):
        employee = request.env['hr.employee'].sudo().browse(employee_id) # Use sudo() for unauthenticated access
        ic(employee)
        if not employee or not employee.avatar_128:
            placeholder_path = request.env['ir.module.module']._get_static_file_path('sd_contacts', 'img/im.jpg') # Get the absolute path
            ic(placeholder_path)
            if placeholder_path:
                with open(placeholder_path, 'rb') as f:  # Open in binary mode
                    image_data = f.read()
                return Response(image_data, content_type='image/jpeg')

        # For employee avatars, use direct_passthrough and Content-Length
        content_type = 'image/png'  # Or image/jpeg, etc. (check your avatars)
        headers = [('Content-Type',
                    content_type)]  # , ('Content-Length', len(employee.avatar_128))]  # Content-Length is optional if you have decoding issues
        return Response(base64.b64decode(employee.avatar_128), headers=headers, direct_passthrough=True)

    @http.route(['/employee/image',
        '/employee/image/<string:xmlid>',
        '/employee/image/<string:xmlid>/<string:filename>',
        '/employee/image/<string:xmlid>/<int:width>x<int:height>',
        '/employee/image/<string:xmlid>/<int:width>x<int:height>/<string:filename>',
        '/employee/image/<string:model>/<int:id>/<string:field>',
        '/employee/image/<string:model>/<int:id>/<string:field>/<string:filename>',
        '/employee/image/<string:model>/<int:id>/<string:field>/<int:width>x<int:height>',
        '/employee/image/<string:model>/<int:id>/<string:field>/<int:width>x<int:height>/<string:filename>',
        '/employee/image/<int:id>',
        '/employee/image/<int:id>/<string:filename>',
        '/employee/image/<int:id>/<int:width>x<int:height>',
        '/employee/image/<int:id>/<int:width>x<int:height>/<string:filename>',
        '/employee/image/<int:id>-<string:unique>',
        '/employee/image/<int:id>-<string:unique>/<string:filename>',
        '/employee/image/<int:id>-<string:unique>/<int:width>x<int:height>',
        '/employee/image/<int:id>-<string:unique>/<int:width>x<int:height>/<string:filename>'], type='http', auth="user")

    def content_image(self, xmlid=None, model='ir.attachment', id=None, field='datas',
                      filename_field='name', unique=None, filename=None, mimetype=None,
                      download=None, width=0, height=0, crop=False, access_token=None,
                      **kwargs):
        # other kwargs are ignored on purpose
        # todo: sudo() is added as a workaround
        #   It is needed to make sure this would not be as a security hole
        #   1- auth is changed from public to user to limit access to log in users
        ic(id)

        return request.env['ir.http'].sudo()._content_image(xmlid=xmlid, model=model, res_id=id, field=field,
            filename_field=filename_field, unique=unique, filename=filename, mimetype=mimetype,
            download=download, width=width, height=height, crop=crop,
            quality=int(kwargs.get('quality', 0)), access_token=access_token)