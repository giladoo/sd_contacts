from odoo import models, fields, api, _
import json
from datetime import datetime, timedelta
import pytz

from odoo.exceptions import ValidationError


class SdContactsAttendanceReport(models.TransientModel):
    _name = 'sd_contacts.attendance_report_wizard'
    # _rec_name = 'employee_id'

    # employee_id = fields.Many2one('hr.employee', default=lambda self: self.env.context.get('default_employee_id', False))
    # employee_name = fields.Char(related='employee_id.name')

    # start_date = fields.Datetime(default=lambda self: datetime.now(pytz.timezone(self._context.get('tz') or 'UTC')),)
    # end_date = fields.Datetime(default=lambda self: datetime.now(pytz.timezone(self._context.get('tz') or 'UTC')),)
    start_date = fields.Datetime(default=lambda self: datetime.now().replace(hour=20, minute=30, second=0, microsecond=0) - timedelta(days=1))
    end_date = fields.Datetime(default=lambda self: datetime.now().replace(hour=20, minute=29, second=59, microsecond=0))
    # TODO: select the gate


    def attendance_report(self):
        read_form = self.read()[0]
        data = {'form_data': read_form}
        print(f"\n {data}")

        return self.env.ref('sd_contacts.attendance_list_report').report_action(self, data=data)

