# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
import json
from jdatetimext import jdatejs
from icecream import ic

class SdContactsHrAttendance(models.Model):
    _inherit = 'hr.attendance'


    def get_attendance(self, employee_id):
        employee_id =  int(employee_id)
        employee = self.env['hr.employee'].sudo().search_read([('id', '=', employee_id)], ['name', 'hr_icon_display'])
        today = fields.Datetime.today()
        attendances = self.sudo().search([('employee_id', '=', employee_id), ('check_in', '>=', today ) ], order='id')

        attendance_times = list([{'id': rec.id,
                                  'check_in': jdatejs(rec.check_in) if rec.check_in else '',
                                  'check_out': jdatejs(rec.check_out) if rec.check_out else ''
                                  } for rec in attendances])

        ic(employee, attendances, today, attendance_times)
        data = {'attendances': 'attendances', 'employee': employee[0]}
        return json.dumps(data)
