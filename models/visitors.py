
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



    def contact_web(self):
        today = datetime.now(pytz.timezone(self.env.context.get('tz', 'Asia/Tehran'))).date()

        visits = self.sudo().search([('check_in', '>=', today)], )

        destination_tz = pytz.timezone(self.env.context.get('tz', 'Asia/Tehran'))
        def local_date(date_time, destination_tz):
            date_time = pytz.utc.localize(date_time).astimezone(destination_tz)
            return jdatetimejs(date_time, '%Y/%m/%d %H:%M')

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