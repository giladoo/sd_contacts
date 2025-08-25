# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api , _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
import pytz
from  jdatetimext import jdatejs
import jdatetime
from odoo import http
from icecream import ic
from itertools import groupby

from collections import defaultdict

class ReportSdContacts(models.AbstractModel):
    _name = 'report.sd_contacts.attendance_list_template'
    _description = 'Attendance List'


    @api.model
    def _get_report_values(self, docids, data=None):
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        DATE_FORMAT = "%Y-%m-%d"
        lang = self.env.user.lang
        data = dict(data)
        ic(data)
        attendances = []
        report_type = data.get('form_data').get('report_type', '')

        gate_ids = data.get('form_data').get('gate')
        gates = self.env['sd_contacts.gate_info'].browse(gate_ids)
        location = data.get('form_data').get('location')

        if report_type == 'daily':
            start_date = data.get('form_data').get('daily_start')
            end_date = data.get('form_data').get('daily_end')
            # todo: timezone
            start_date = datetime.strptime(start_date, DATE_FORMAT)
            end_date = datetime.strptime(end_date, DATE_FORMAT) + timedelta(days=1)
            ic(start_date, end_date)
            domain = ['&', '|',
                      ('check_in', '>=', start_date ),
                      ('check_out', '>=', start_date ),
                      '|',
                      ('check_in', '<', end_date ),
                      ('check_out', '<', end_date ),
                      ]
            attendances = self.env['hr.attendance'].search(domain)
            if location:
                attendances = list([rec for rec in attendances if rec.in_gate.location == location[0] or rec.out_gate.location == location[0]])
            if gate_ids:
                attendances = list([rec for rec in attendances if rec.in_gate in gate_ids or rec.out_gate in gate_ids])
        elif report_type == 'aa':
            start_date = data.get('form_data').get('start_date')
            end_date = data.get('form_data').get('end_date')
            gate = data.get('form_data').get('gate')
            start_date = datetime.strptime(start_date, DATETIME_FORMAT)
            end_date = datetime.strptime(end_date, DATETIME_FORMAT)
            data = {'gate': gate[1],
                    'start_date': self.date_converter(start_date, lang),
                    'end_date': self.date_converter(end_date, lang)
                    }
            ic(type(start_date))
            attendances = self.env['hr.attendance'].search(['&', '|',
                                                            ('check_in', '>=', start_date ),
                                                            ('check_out', '>=', start_date ),
                                                            '|',
                                                            ('check_in', '<=', end_date ),
                                                            ('check_out', '<=', end_date ),
                                                            ('in_gate', '=', gate[0])

                                                            ])
        ic(attendances)
        attendances = list([{
            'name': rec.employee_id.name,
            'check_in': self.date_converter(rec.check_in, lang) if rec.check_in else '',
            'check_out': self.date_converter(rec.check_out, lang) if rec.check_out else '',
            'in_gate': rec.in_gate.name,
            'out_gate': rec.out_gate.name,

        }
            for rec in attendances])

        attendances.sort(key=lambda x: x['name'])
        grouped = {
            key: list(group)
            for key, group in groupby(attendances, key=lambda x: x['name'])
        }

        ic(grouped)
        docs = []
        all_data1 = {

            'docids': docids,
            'docs': docs,
            # 'data': data,
            'gates': gates,
            'location': location,
            'attendances': attendances,
            'grouped': grouped,

        }
        # ic(all_data)
        return all_data1


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