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


class ReportSdContacts(models.AbstractModel):
    _name = 'report.sd_contacts.attendance_list_template'
    _description = 'Attendance List'


    @api.model
    def _get_report_values(self, docids, data=None):
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        lang = self.env.user.lang
        print(f"\n docids: {docids} data:")
        data = dict(data)
        ic(data, self.env.user.lang)
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
        attendances = list([{
                            'name': rec.employee_id.name,
                            'check_in': self.date_converter(rec.check_in, lang) if rec.check_in else '',
                            'check_out': self.date_converter(rec.check_out, lang) if rec.check_out else '',

                                     }
                                    for rec in attendances])

        ic(attendances)

        docs = []
        return{

            'docids': docids,
            'docs': docs,
            'data': data,
            'attendances': attendances,
        }


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