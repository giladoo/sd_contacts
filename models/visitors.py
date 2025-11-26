
from odoo import models, fields, api, _
from datetime import datetime
import jdatetime
from jdatetimext import jdatejs, jdatetimejs
import pytz
import json
from odoo.api import ValuesType, Self
from odoo.exceptions import ValidationError

class SdContactsVisitors(models.Model):
    _name = "sd_contacts.visitors"
    _description = "Visitors data"
    _rec_names_search = ['name', 'national_id']

    name = fields.Char(required=True)
    national_id = fields.Char()
    mobile_no = fields.Char()
    # company_id = fields.Many2one("res.company")

    _sql_constraints = [('national_id_uniq', 'unique (national_id)', "National ID MUST be unique!")]

    @api.depends('name', 'national_id',)
    def _compute_display_name(self):
        super()._compute_display_name()
        for rec in self:
            national_id = ' - ' + rec.national_id if rec.national_id else ''
            rec.display_name = f"{rec.name}{national_id}"


class SdContactsVisits(models.Model):
    _name = "sd_contacts.visits"
    _description = "Visits data"

    name = fields.Many2one("sd_contacts.visitors",required=True)
    check_in = fields.Datetime(string="Check In", default=fields.Datetime.now, required=True, tracking=True)
    check_out = fields.Datetime(string="Check Out", tracking=True)
    in_gate = fields.Many2one('sd_contacts.gate_info')
    out_gate = fields.Many2one('sd_contacts.gate_info')
    employee_id = fields.Many2one("hr.employee")
    description = fields.Char()

    def set_attendance(self, visitor_id, gate_id):
        visitor_id = int(visitor_id)
        gate_id = int(gate_id)

        visit_id = self.search([('name', '=', visitor_id), ('check_out', '=', False)])
        if len(visit_id):
            visit_id.write({'check_out': datetime.now(), 'out_gate': int(gate_id)})
        else:
            visit = self.search([('name', '=', visitor_id), ], order="id desc", limit=1)
            if len(visit):
                visit_id = self.create({'name': visitor_id,
                             'employee_id': visit.employee_id.id if visit.employee_id else False,
                             'in_gate': gate_id,
                             })
            else:
                visit_id = self.create({'name': visitor_id, 'in_gate': gate_id,})

        return visit_id.id


    def set_check_out(self, visit_id, gate_id):
        check_out_done = False
        visit_id = int(visit_id)
        gate_id = int(gate_id)
        visit = self.search([('id', '=', visit_id)])
        if visit:
            return visit.write({'check_out': datetime.now(), 'out_gate': gate_id})

    def contact_web(self, present='presents'):
        destination_tz = pytz.timezone(self.env.context.get('tz', 'Asia/Tehran'))
        def local_date(date_time, destination_tz):
            date_time = pytz.utc.localize(date_time).astimezone(destination_tz)
            return jdatetimejs(date_time, '%Y/%m/%d %H:%M')

        utc_now = datetime.now()
        start_of_day_local = utc_now.astimezone(pytz.timezone(self.env.context.get('tz', 'Asia/Tehran')))
        start_of_day_local_1 = start_of_day_local.replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_day_local_2 = start_of_day_local_1.astimezone(pytz.timezone('UTC'))
        start_of_day = start_of_day_local_2.replace(tzinfo=None)

        if present == 'all':
            domain = ['|', '|',
                      ('check_in', '>=', start_of_day),
                      ('check_out', '>=', start_of_day),
                      ('check_out', '=', False) ]
            order = "name, check_in desc"
        else:
            domain = [('check_out', '=', False)]
            order = "check_in desc"
        visits = self.sudo().search(domain, order=order )

        visits_list = list([
            {
                'id': rec.id,
                'name': rec.name.name,
                'national_id': rec.name.national_id,
                'mobile_no': rec.name.mobile_no,
                'employee': rec.employee_id.name,
                'check_in': local_date(rec.check_in, destination_tz),
                'check_out': local_date(rec.check_out, destination_tz) if rec.check_out else '',
            }
            for rec in visits
        ])
        return json.dumps({
            'visits_list': visits_list,
        })

    def get_attendance(self, visit_id):
        # print(f">>>>>>>>>>\nvisit_id: {visit_id}")
        visit_id = self.browse(int(visit_id))
        visitor_id = visit_id.name
        # visitor_name = 'Arash'
        # visit_times = [{'check_in': ('', '12:10'), 'check_out': ('', '13:30'),}]

        utc_now = datetime.now()
        start_of_day_local = utc_now.astimezone(pytz.timezone(self.env.context.get('tz', 'Asia/Tehran')))
        start_of_day_local_1 = start_of_day_local.replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_day_local_2 = start_of_day_local_1.astimezone(pytz.timezone('UTC'))
        start_of_day = start_of_day_local_2.replace(tzinfo=None)

        visits = self.sudo().search([('name', '=', visitor_id.id),
                                          '|','|',
                                          ('check_in', '>=', start_of_day ) ,
                                          ('check_out', '>=', start_of_day ) ,
                                          ('check_out', '=', False ) ,
                                          ], order='id')

        visit_times = list([{'id': rec.id,
                                  'check_in': self.get_time(rec.check_in, month=True if rec.check_in < start_of_day else False),
                                  'check_out': self.get_time(rec.check_out),
                                  'in_gate': rec.in_gate.code,
                                  'out_gate': rec.out_gate.code,
                                  } for rec in visits])
        is_operator = self.env.user._has_group('sd_contacts.group_sd_contacts_operators')
        return json.dumps({
            'visitor': {'id': visitor_id.id,
                        'name': visitor_id.name,
                        'national_id': visitor_id.national_id or '',
                        'mobile_no': visitor_id.mobile_no or '',
                        },
            'visit_times': visit_times,
            'is_operator': is_operator,
        })

    def get_time(self, date_time, user_tz='Asia/Tehran', month=False):
        if isinstance(date_time, datetime):
            dtime = date_time.astimezone(pytz.timezone(user_tz)).strftime("%H:%M")
            # todo : gregorian needed
            if month:
                jdatetime.set_locale(jdatetime.FA_LOCALE)
                ddate = jdatetime.date.fromgregorian(date=date_time.astimezone(pytz.timezone(user_tz))).strftime("%b %d")
                res =  (ddate, dtime)
            else:
                res = ('', dtime)

        else:
            res =  ('', '')

        return res


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