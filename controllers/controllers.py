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

