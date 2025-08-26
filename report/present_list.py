# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, tools , _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
import pytz
from  jdatetimext import jdatejs
import jdatetime
from odoo import http
from icecream import ic
from itertools import groupby

from collections import defaultdict

class ReportSdContactsPresentList(models.AbstractModel):
    _name = 'report.sd_contacts.present_list_template'
    _description = 'Present List'


    @api.model
    def _get_report_values(self, docids, data=None):
        DATETIME_FORMAT = "%Y-%m-%d  %H:%M:%S"
        DATE_FORMAT = "%Y-%m-%d"
        DATE_FORMAT_J = "%Y/%m/%d"
        TIME_FORMAT = "%H:%M:%S"
        lang = self.env.user.lang
        is_fa = lang == 'fa_IR'
        data = dict(data)
        location_ids = data.get('locations', False)
        # todo: temporary location
        location_ids = [2]

        att_domain = [('check_out', '=', False),]
        if location_ids:
            locations = self.env['hr.work.location'].browse(location_ids)
            att_domain = att_domain + [('in_gate.location', 'in', location_ids),]
        else:
            locations = self.env['hr.work.location'].search([])

        tz = pytz.timezone(self._context.get('tz', 'UTC'))
        date_now = fields.Datetime.now().astimezone(tz)
        date_now_s = f"{jdatejs(date_now, DATE_FORMAT_J)}  {date_now.strftime(TIME_FORMAT)}" \
            if is_fa else date_now.strftime(DATETIME_FORMAT)

        att_employees = self.env['hr.attendance'].search(att_domain )
        att = dict(tools.groupby(att_employees, key=lambda a: a.in_gate.location))
        grouped_att = dict({k.name: v for k, v in att.items()})
        docs = []
        all_data_1 = {

            'docids': docids,
            'docs': docs,
            'lang': lang,
            'locations': list([rec for rec in grouped_att]),
            'date_now_s': date_now_s,
            'att_employees': att_employees,
            'grouped_att': grouped_att,
            'count': len(att_employees)

        }
        ic(all_data_1)
        return all_data_1


    def date_converter(self, date_time, lang):
        user_timezone = pytz.timezone(self.env.user.tz or self.env.context.get('tz', 'utc'))
        date_time = date_time.astimezone(user_timezone)

        # print(f">>>>>>>>>>>>>>>>>>>> 1   {user_timezone} date_time: \ndate_time : {date_time}\nlocal_time: {local_time}\n")
        if lang == 'fa_IR':
            date_time = jdatetime.datetime.fromgregorian(datetime=date_time)
            date_time = {'date': date_time.strftime("%Y/%m/%d"),
                  'time': date_time.strftime("%H:%M:%S")}
        else:
            date_time = {'date': date_time.strftime("%Y/%m/%d"),
                        'time': date_time.strftime("%H:%M:%S")}
        return date_time['date'] + ' ' + date_time['time']