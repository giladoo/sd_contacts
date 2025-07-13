# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
import json
from datetime import datetime, timedelta
import jdatetime
from jdatetimext import jdatejs
from icecream import ic
import pytz


class SdContactsHrAttendance(models.Model):
    _inherit = "hr.attendance"


    def get_last_attendances(self, last_attendances_items_count=10):
        user_tz = self.env.context.get('tz', 'Asia/Tehran')
        # TODO: last_attendances_items_count can be setby user
        last_attendances = self.sudo().search_read([], [ 'employee_id', 'check_in', 'check_out'], limit=last_attendances_items_count, order='write_date desc')
        last_attendance_check_in = list([{k if k != 'check_in' else 'time': v for k, v in rec.items() if k != "check_out" } for rec in last_attendances])
        last_attendance_check_in = list([{**rec, 'dir': 'in'} for rec in last_attendance_check_in])
        last_attendance_check_out = list([{k if k != 'check_out' else 'time': v for k, v in rec.items() if k != "check_in"} for rec in last_attendances])
        last_attendance_check_out = list([{**rec, 'dir': 'out'} for rec in last_attendance_check_out if rec['time']])
        last_attendances_time = last_attendance_check_in + last_attendance_check_out
        last_attendances_time.sort(key=lambda item: item['time'], reverse=True)
        last_attendances_time = list([self.get_record_time(rec) for rec in last_attendances_time[:last_attendances_items_count]])

        # presents = self.env['hr.employee'].sudo().search_count([('hr_icon_display', '=', "presence_present")])
        # absence = self.env['hr.employee'].sudo().search_count([('hr_icon_display', '!=', "presence_present")])
        employees = self.env['hr.employee'].sudo().search_read([], ['hr_icon_display'])
        presents = len(list([rec for rec in employees if rec['hr_icon_display'] == 'presence_present']))
        absence = len(list([rec for rec in employees if rec['hr_icon_display'] != 'presence_present']))
        today = jdatejs(datetime.now().astimezone(pytz.timezone(user_tz)), '%Y/%m/%d')

        # ic(employees)





        all_emps = presents + absence
        return json.dumps({'last_attendances_time': last_attendances_time,
                           'presents': presents,
                           'absence': absence,
                           'all_emps': all_emps,
                           'today': today,
                           })


    def remove_key(self, rec, key):
        del rec[key]
        return rec

    def get_attendance(self, employee_id):
        user_tz = self.env.context.get('tz', 'Asia/Tehran')

        employee_id =  int(employee_id)

        employee = self.env['hr.employee'].sudo().search_read([('id', '=', employee_id)],
                                                              ['name', 'hr_icon_display'])
        today = fields.Datetime.today()
        # today = today.astimezone(pytz.timezone(user_tz))

        attendances = self.sudo().search([('employee_id', '=', employee_id), ('check_in', '>=', today ) ], order='id')

        attendance_times = list([{'id': rec.id,
                                  'check_in': self.get_time(rec.check_in),
                                  'check_out': self.get_time(rec.check_out)
                                  } for rec in attendances])

        # ic(employee, attendances, today, attendance_times)
        employee_leaves = self.env['hr.leave'].sudo().search([('employee_id', '=', employee_id),
                                                     ('date_from', '<=', today  + timedelta(days=1)),
                                                     ('date_to', '>=', today),
                                                     ], order='id')
        # print(f"$$$$$$$$$$$ LEAVE:\n {employee_leaves}")
        leaves = []
        for leave in employee_leaves:
            time_of_date_from = leave.date_from.astimezone(pytz.timezone(user_tz)).strftime("%H:%M")
            time_of_date_to = leave.date_to.astimezone(pytz.timezone(user_tz)).strftime("%H:%M")

            leave_start = '00:00' if leave.date_from < today else time_of_date_from
            leave_end = '23:59' if leave.date_to > today + timedelta(days=1) else time_of_date_to
            if leave.state == 'validate':
                state_icon = 'fa-check'
            elif leave.state == 'confirm':
                state_icon = 'fa-question'
            elif leave.state in ['cancel', 'refuse']:
                state_icon = 'fa-close'
            else:
                state_icon = 'fa-question'
            leaves.append({
                            'leave_type': leave.holiday_status_id.display_name,
                           'start': leave_start,
                           'end': leave_end,
                           'state_icon': state_icon,
                           })
            # print(f"{today}\n{leave.date_from} {leave_start} {time_of_date_from}\n{leave.date_to} {leave_end} {time_of_date_to}")
        # leaves = [{'leave_type': 'Leave 1', 'start': '8:00', 'end': '9:01'}]

        data = {'attendances': attendance_times, 'employee': employee[0], 'leaves': leaves}
        return json.dumps(data)

    def set_attendance(self, employee_id):
        employee_id =  int(employee_id)

        employee = self.env['hr.employee'].sudo().browse(employee_id)
        employee_att = employee._attendance_action_change()
        # ic(employee_id, employee_att)

    def get_time(self, date_time, user_tz='Asia/Tehran', month=False):
        if isinstance(date_time, datetime):
            dtime = date_time.astimezone(pytz.timezone(user_tz)).strftime("%H:%M")
            # todo : gregorian needed
            if month:
                jdatetime.set_locale(jdatetime.FA_LOCALE)
                ddate = jdatetime.date.fromgregorian(date=date_time.astimezone(pytz.timezone(user_tz))).strftime("%b %d")
                res =  (ddate, dtime)
            else:
                res = dtime
        else:
            res =  ''

        return res

    def get_record_checkin_checkout_time(self, rec):
        rec['check_in'] = self.get_time(rec['check_in'])
        rec['check_out'] = self.get_time(rec['check_out'])
        return rec


    def get_record_time(self, rec):
        rec['time'] = self.get_time(rec['time'], 'Asia/Tehran', True)
        return rec