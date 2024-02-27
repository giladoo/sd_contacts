# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.modules.module import get_module_resource
from odoo.addons.http_routing.models.ir_http import url_for
from odoo.tools import ustr
from datetime import datetime, timedelta
# import datetime
from colorama import Fore
import jdatetime
import logging
import json
logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG)
logger = logging.getLogger(__name__)



# #######################################################################################
class SdContactsController(http.Controller):

    # #######################################################################################
    @http.route('/employee/contacts/', type='http', auth="user", website=True)
    def sd_employee_phone_list(self, **kwargs):
        return http.request.render('sd_contacts.employee_contacts', { })


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
        '/employee/image/<int:id>-<string:unique>/<int:width>x<int:height>/<string:filename>'], type='http', auth="public")
    def content_image(self, xmlid=None, model='ir.attachment', id=None, field='datas',
                      filename_field='name', unique=None, filename=None, mimetype=None,
                      download=None, width=0, height=0, crop=False, access_token=None,
                      **kwargs):
        # other kwargs are ignored on purpose
        # todo: sudo() is added as a workaround
        #   It is needed to make sure this would not be as a security hole

        return request.env['ir.http'].sudo()._content_image(xmlid=xmlid, model=model, res_id=id, field=field,
            filename_field=filename_field, unique=unique, filename=filename, mimetype=mimetype,
            download=download, width=width, height=height, crop=crop,
            quality=int(kwargs.get('quality', 0)), access_token=access_token)