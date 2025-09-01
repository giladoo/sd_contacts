from odoo import models, fields, api, _
import json
import datetime
import pytz
from odoo.tools import date_utils, format_date

from odoo.exceptions import ValidationError


class SdContactsAttendanceReport(models.TransientModel):
    _name = 'sd_contacts.attendance_report_wizard'
    _description = ""
    # _rec_name = 'employee_id'
    report_type = fields.Selection([('daily', 'Daily')], default='daily', required=True)
    location = fields.Many2one('hr.work.location')
    gate = fields.Many2many('sd_contacts.gate_info')
    # employee_id = fields.Many2one('hr.employee', default=lambda self: self.env.context.get('default_employee_id', False))
    # employee_name = fields.Char(related='employee_id.name')
    daily_start = fields.Date(default=lambda self: fields.datetime.today(),)
    daily_end = fields.Date(default=lambda self: fields.datetime.today(),)

    start_date = fields.Datetime(default=lambda self: date_utils.start_of(fields.Date.context_today(self), 'day'))
    # end_date = fields.Datetime(default=lambda self: fields.datetime.now(pytz.timezone(self.env.user.tz)).replace(tzinfo=None),)
    end_date = fields.Datetime(default=lambda self: fields.Date.context_today(self))
    # start_date = fields.Datetime(default=lambda self: datetime.now().replace(hour=20, minute=30, second=0, microsecond=0) - timedelta(days=1))
    # end_date = fields.Datetime(default=lambda self: datetime.now().replace(hour=20, minute=29, second=59, microsecond=0))
    # TODO: select the gate


    def attendance_report(self):
        read_form = self.read()[0]
        data = {'form_data': read_form}
        # print(f"\n {data}")

        return self.env.ref('sd_contacts.attendance_list_report').report_action(self, data=data)

