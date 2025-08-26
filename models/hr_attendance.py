# -*- coding: utf-8 -*-
from custom.PG.jdatetimext.jdatetimext.jdate_utils import DATETIME_FORMAT
from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
import json
from datetime import datetime, timedelta
import jdatetime
from jdatetimext import jdatejs
from icecream import ic
import pytz
from odoo.exceptions import ValidationError
import base64

class SdContactsHrAttendance(models.Model):
    _inherit = "hr.attendance"

    in_gate = fields.Many2one('sd_contacts.gate_info')
    out_gate = fields.Many2one('sd_contacts.gate_info')
    work_location_id = fields.Many2one(related="employee_id.work_location_id")



    def get_last_attendances(self, last_attendances_items_count=10, location=1):
        user_tz = self.env.context.get('tz', 'Asia/Tehran')
        start_date = datetime.now(pytz.timezone(self.env.context.get('tz', 'Asia/Tehran'))).date()

        employee_domain = [('work_location_id', '=', int(location))]
        gates_location = self.env['sd_contacts.gate_info'].search([('location', '=', int(location))])
        gates_location_ids = gates_location.ids if gates_location else []
        attendance_domain = ['|', ('in_gate', 'in', gates_location_ids),('out_gate', 'in', gates_location_ids), ]
        gates = self.env['sd_contacts.gate_info'].search_read([], ['name', 'code'])
        # TODO: last_attendances_items_count can be setby user
        last_attendances = self.sudo().search_read(attendance_domain, [ 'employee_id', 'check_in', 'check_out', 'in_gate', 'out_gate',], limit=last_attendances_items_count, order='write_date desc')
        last_attendance_check_in = list([{k if k != 'check_in' else 'time': v for k, v in rec.items() if k != "check_out" } for rec in last_attendances])
        lattendances = self.sudo().search(attendance_domain, limit=last_attendances_items_count, order='write_date desc')

        # ic(lattendances[0].employee_id.hr_icon_display)
        # ic(len(last_attendance_check_in))
        last_attendance_check_in = list([{**rec, 'dir': 'in', 'gate': rec['in_gate'] and list(filter(lambda x : x['id'] == rec['in_gate'][0], gates))[0]['name']}
                                         for rec in last_attendance_check_in])
        last_attendance_check_out = list([{k if k != 'check_out' else 'time': v for k, v in rec.items() if k != "check_in"} for rec in last_attendances])
        last_attendance_check_out = list([{**rec, 'dir': 'out', 'gate': rec['out_gate'] and list(filter(lambda x : x['id'] == rec['out_gate'][0], gates))[0]['name'] }
                                          for rec in last_attendance_check_out if rec['time']])
        last_attendances_time = last_attendance_check_in + last_attendance_check_out
        for d in last_attendances_time:
            d.pop('in_gate', None)
            d.pop('out_gate', None)
        last_attendances_time.sort(key=lambda item: item['time'], reverse=True)
        last_attendances_time = list([self.get_record_time(rec) for rec in last_attendances_time[:last_attendances_items_count]])
        # ic(last_attendances_time[:3])
        # {'dir': 'out',
        #  'employee_id': (93, 'افسانه آتش افروز'),
        #  'id': 33,
        #  'in_gate': (2, 'درب دوم'),
        #  'out_gate': (2, 'درب دوم'),
        #  'time': ('مرداد 29', '16:29')},
        # presents = self.env['hr.employee'].sudo().search_count([('hr_icon_display', '=', "presence_present")])
        # absence = self.env['hr.employee'].sudo().search_count([('hr_icon_display', '!=', "presence_present")])
        employees = self.env['hr.employee'].sudo().search_count(employee_domain, )
        # presents = len(list([rec for rec in employees if rec['hr_icon_display'] == 'presence_present']))
        # absence = len(list([rec for rec in employees if rec['hr_icon_display'] != 'presence_present']))
        today = jdatejs(datetime.now().astimezone(pytz.timezone(user_tz)), '%Y/%m/%d')

        DATETIEM_FORMAT = "%Y-%m-%d %H:%M:%S"
        selected_date = datetime.now(pytz.timezone(self.env.context.get('tz', 'Asia/Tehran')))
        # selected_date = datetime.strptime("2025-08-23 14:14:14", DATETIEM_FORMAT)
        start_date = (selected_date - timedelta(days=1)).replace(hour=20, minute=30, second=0, microsecond=0)
        start_date_s = start_date.strftime(DATETIEM_FORMAT)
        end_date = start_date + timedelta(days=1)
        end_date_s = end_date.strftime(DATETIEM_FORMAT)
        gates = self.env['sd_contacts.gate_info'].sudo().search([('location', '=', location)])
        gates_loc = gates.ids if gates else []
        local_attendances = self.env['hr.attendance'].sudo().search_read([
            ('employee_id.work_location_id', '=', location),
            ('in_gate', 'in', gates_loc),
            ('check_out', '=', False),
        ], ['employee_id'])
        local_employee_ids = list([rec['employee_id'][0] for rec in local_attendances ])
        local_attendances = len(local_attendances)

        site_attendances = self.env['hr.attendance'].sudo().search_read([
            ('employee_id.work_location_id', '=', location),
            ('in_gate', 'not in', gates_loc),
            ('check_out', '=', False),
        ], ['employee_id'])
        site_employee_ids = list([rec['employee_id'][0] for rec in site_attendances ])
        site_attendances = len(site_attendances)
        left_attendances = self.env['hr.attendance'].sudo().search_read([
            ('employee_id', 'not in', local_employee_ids + site_employee_ids ),
            ('employee_id.work_location_id', '=', location),
            ('check_out', '>=', start_date_s),
            ('check_out', '<', end_date_s),
        ], ['employee_id'])
        left_attendances = len(list({rec['employee_id'][0] for rec in left_attendances}))

        # print(f"{start_date}\n{end_date} \n all_attendances:{local_attendances}\n site_attendances: {site_attendances}")


        # print(f"{start_date}\n{end_date} \n gates_loc:{gates_loc}")
        guest_attendances = self.env['hr.attendance'].sudo().search_read([
            ('employee_id.work_location_id', '!=', location),
            ('in_gate', 'in', gates_loc),
            '|','|',
            '&',
            ('check_in', '>=', start_date_s),
            ('check_in', '<', end_date_s),
            '&',
            ('check_out', '>=', start_date_s),
            ('check_out', '<', end_date_s),
            ('check_out', '=', False),
        ],
            ['id', 'employee_id', 'check_in', 'check_out', 'in_gate', 'out_gate']
        )
        all_guest = len(guest_attendances)
        present_guests = len(list([rec for rec in guest_attendances if not rec['check_out']]))
        leave_guests = all_guest - present_guests
        # print(f"len(attendances):{len(guest_attendances)}\n{guest_attendances} ")
        counts = {
            'local_attendances': local_attendances,
            'site_attendances': site_attendances,
            'left_attendances': left_attendances,
            'absence': employees - local_attendances - site_attendances - left_attendances,
            'all_emps':employees,
            'present_guests': present_guests,
            'leave_guests': leave_guests,
            'all_guest': all_guest,
        }



        return json.dumps({'last_attendances_time': last_attendances_time,
                            'counts': counts,
                           'today': today,
                           })

    def get_gates(self):
        # todo: you need to restrict users to have access to their own gates only
        gates = self.env['sd_contacts.gate_info'].sudo().search_read([], ['name', 'code', 'location'])
        return json.dumps({'gates': gates, })



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
                                  'check_out': self.get_time(rec.check_out),
                                  'in_gate': rec.in_gate.code,
                                  'out_gate': rec.out_gate.code,
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

        is_operator = self.env.user._has_group('sd_contacts.group_sd_contacts_operators')
        data = {'attendances': attendance_times, 'employee': employee[0], 'leaves': leaves, 'is_operator': is_operator}
        return json.dumps(data)

    def set_attendance_btn(self):
        if not self.env.user._has_group('sd_contacts.group_sd_contacts_operators'):
            return
        context = self.env.context
        gate_id = context.get('gate_id', False)
        employee_id = context.get('employee_id', False)
        if employee_id and gate_id:
            last_emp_attendance = self.search([('employee_id', '=', employee_id), ('check_out', '=', False)])
            if last_emp_attendance:
                self.set_attendance(employee_id, gate_id)

    def set_attendance(self, employee_id, gate_id):
        if not self.env.user._has_group('sd_contacts.group_sd_contacts_operators'):
            return
        employee_id =  int(employee_id)
        gate = self.env['sd_contacts.gate_info'].browse(int(gate_id))
        last_emp_attendance = self.search([('employee_id', '=', employee_id), ('check_out', '=', False)])
        if last_emp_attendance and last_emp_attendance.in_gate.location.id != gate.location.id:
            raise ValidationError(_(f"Location error; In location was: {last_emp_attendance.in_gate.location.name}"))

        employee = self.env['hr.employee'].sudo().browse(employee_id)
        employee_att = employee._attendance_action_change()
        # ic(employee_id, employee_att)
        if employee_att.check_out:
            employee_att.out_gate = gate_id
        else:
            employee_att.in_gate = gate_id
        # ic(employee_att.out_gate, employee_att.in_gate)

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

    def send_emergency(self, location):
        # ic(location)
        DATETIME_FORMAT = "%Y%m%d_%H%M%S"
        is_fa = self.env.user.lang == 'fa_IR'
        tz = pytz.timezone(self._context.get('tz') or 'UTC')
        file_datetime = fields.Datetime.now().astimezone(tz)
        # ic(file_datetime)
        file_datetime_s = f'{jdatejs(file_datetime, "%Y%m%d")}_{file_datetime.strftime("%H%M%S")}' \
            if is_fa else file_datetime.strftime(DATETIME_FORMAT)
        location = self.env['hr.work.location'].browse(location)
        email_recipients = location.emergency_emails
        recipients = list([rec.private_email for rec in email_recipients if rec.private_email])
        # ic(recipients)
        # TODO: create pdf file list
        report_obj = self.env['ir.actions.report']
        pdf_content, _ = report_obj._render_qweb_pdf('sd_contacts.present_list_report', [location.id])

        attachment = self.env['ir.attachment'].create({
            'name': f'kpe_{file_datetime_s}_[{location.name}].pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'mimetype': 'application/pdf',
            'res_model': 'hr.attachment',
        })

        mail_values = {
            'subject': f'KPE Emergency EXIT {file_datetime_s} [{location.name}]',
            'body_html': f'<p>KPE Emergency EXIT {file_datetime_s} [{location.name}]</p>',
            'email_to': ','.join(recipients),
            'email_from': 'portal@kpe.ir',
            'attachment_ids': [(6, 0, [attachment.id])],

        }
        send_result = self.env['mail.mail'].create(mail_values).send()
        ic(send_result)

