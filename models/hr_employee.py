# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
import json
class HrEmployeeSdContacts(models.Model):
    _inherit = 'hr.employee'

    show_contact = fields.Boolean(default=True)
    def contact_web(self):
        # company_id = self.env.user.company_id
        # company_ids = self.env.user.company_ids
        if self.env.is_admin():
            company_ids = self.env['res.company'].search([])
        else:
            # todo: error psycopg2.errors.UndefinedTable: relation "res_company_res_users_rel" does not exist
            # company_ids = self.env.user.sd_contacts_companies
            company_ids = self.env['res.company'].sudo().search([])
        employee_list = self.sudo().search([('company_id', 'in', company_ids.ids), ('show_contact', '=', True)], order='sequence')
#         print(f'''
#
#                 {self.env.user.name}  is admin: {self.env.is_admin()}
#                 {company_ids}
#                 employee_list: {len(employee_list)}
#
# ''')
        contact_list = list([
            {
                'id' : rec.id,
                'name' : rec.name,
                'work_phone' : rec.work_phone,
                'work_email' : rec.work_email,
                'work_location' : rec.work_location_id.name,
                'department' : rec.department_id.name,
                'job_title' : rec.job_title,
                'company' : rec.company_id.name,
                'present' : rec.hr_presence_state,
                'im_status' : rec.user_id.im_status,
             }
            for rec in employee_list
        ])

        location_list = list({
                    rec.work_location_id.name for rec in employee_list if rec.work_location_id
                    })
        location_list.insert(0, _('All'))

        department_list = list({
                    rec.department_id.name for rec in employee_list if rec.department_id
                    })
        department_list.insert(0, _('All'))

        company_list = list([
            rec.name
            for rec in company_ids
        ])
        return json.dumps({'contact_list': contact_list,
                           'company_list': company_list,
                           'location_list': location_list,
                           'department_list': department_list,
                           })