# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api , _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
import pytz
from  jdatetimext import jdatejs
from odoo import http
from icecream import ic


class ReportSdContacts(models.AbstractModel):
    _name = 'report.sd_contacts.attendance_list_template'
    _description = 'Attendance List'


    @api.model
    def _get_report_values(self, docids, data=None):
        print(f"\n docids: {docids} data: {data}")

        docs = []
        return{
            'docids': docids,
            'docs': docs,
        }

