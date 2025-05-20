# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
import json
from datetime import datetime
import jdatetime
from jdatetimext import jdatejs
from icecream import ic
import pytz


class SdContactsAttendance(models.Model):
    _inherit = "sd_contacts.attendance"
    _description = ""

    partner_id = fields.Many2one('res.partner')
    check_in = fields.Datetime(default=lambda self: datetime.now(pytz.timezone(self._context.get('tz') or 'UTC')),)

    check_out = fields.Datetime()