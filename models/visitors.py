
from odoo import models, fields, api, _
from datetime import datetime
from jdatetimext import jdatejs, jdatetimejs
import pytz
import json

from odoo.api import ValuesType, Self
from odoo.exceptions import ValidationError

class SdContactsVisitors(models.Model):
    _name = "sd_contacts.visitors"
    _description = "Visitors data"

    name = fields.Char(required=True)
    national_id = fields.Char()
    mobile_no = fields.Char()
    # company_id = fields.Many2one("res.company")




class SdContactsVisits(models.Model):
    _name = "sd_contacts.visits"
    _description = "Visits data"

    name = fields.Many2one("sd_contacts.visitors",required=True)
    check_in = fields.Datetime(string="Check In", default=fields.Datetime.now, required=True, tracking=True)
    check_out = fields.Datetime(string="Check Out", tracking=True)
    employee_id = fields.Many2one("hr.employee")
    description = fields.Char()

    def set_check_out(self, visit_id):
        check_out_done = False
        visit = self.search([('id', '=', int(visit_id))])
        if visit:
            check_out_done = visit.write({'check_out': datetime.now()})
        print(f"\n ................... \ncheck_out_done {check_out_done}")



    def contact_web(self, present='presents'):
        destination_tz = pytz.timezone(self.env.context.get('tz', 'Asia/Tehran'))
        def local_date(date_time, destination_tz):
            date_time = pytz.utc.localize(date_time).astimezone(destination_tz)
            return jdatetimejs(date_time, '%Y/%m/%d %H:%M')

        today = datetime.now(pytz.timezone(self.env.context.get('tz', 'Asia/Tehran'))).date()

        # utc_now = fields.Datetime.now()
        # tz_name = self.env.user.tz or 'UTC'
        # tz = pytz.timezone(tz_name)
        # local_dt = utc_now.astimezone(tz)
        # start_of_day = utc_now.replace(hour=0, minute=0, second=0, microsecond=0)
        # start_of_day_local = pytz.utc.localize(start_of_day).astimezone(destination_tz)

        utc_now = datetime.now()
        start_of_day_local = utc_now.astimezone(pytz.timezone(self.env.context.get('tz', 'Asia/Tehran')))
        start_of_day_local_1 = start_of_day_local.replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_day_local_2 = start_of_day_local_1.astimezone(pytz.timezone('UTC'))
        start_of_day = start_of_day_local_2.replace(tzinfo=None)

        domain = [ ('check_out', '=', False)]
        order = "check_in desc"
        if present == 'all':
            domain = ['|', ('check_in', '>=', start_of_day), ('check_out', '=', False) ]
            order = "name, check_in desc"
        # print(f"<<<<<<<<<<<<<<<< \npresent: {present} \ndomain: {domain}\norder: {order}")
        visits = self.sudo().search(domain, order=order )
        # value = fields.Datetime.context_timestamp(self, value)
        # print(f"ddddddddddddddddddddd\n"
        #       f"check_in:              {visits[0].check_in}\n"
        #       f"utc_now:               {utc_now}\n"
        #       f"start_of_day_local:    {start_of_day_local}\n"
        #       f"start_of_day_local_1:  {start_of_day_local_1}\n"
        #       f"start_of_day_local_2:  {start_of_day_local_2}\n"
        #       f"start_of_day :         {start_of_day}")
        # TODO:  check_in between 00:00 to 03:30 are not shown in today
        #  today: 2025-11-25
        #  check_in: 2025-11-24 20:44:56


        visits_list = list([
            {
                'id': rec.id,
                'name': rec.name.name,
                'employee': rec.employee_id.name,
                'check_in': local_date(rec.check_in, destination_tz),
                'check_out': local_date(rec.check_out, destination_tz) if rec.check_out else '',
            }
            for rec in visits
        ])
        return json.dumps({
            'visits_list': visits_list,
        })

    @api.model_create_multi
    def create(self, vals_list: list[ValuesType]) -> Self:
        for vals in vals_list:
            # print(f"\n vlas: {vals}\n")
            if not vals.get('check_out', False):
                visitor = vals.get('name', False)
                exists = self.search_count([('name', '=', visitor), ('check_out', '=', False)])
                if exists:
                    raise ValidationError(f"Visitor is not check out yet!")
            # pass

        return super().create(vals_list)