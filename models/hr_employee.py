# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
import json
from icecream import ic

class HrEmployeeSdContacts(models.Model):
    _inherit = 'hr.employee'

    show_in_contact_list = fields.Boolean(default=True)
    sequence = fields.Integer(default=10000)


    def contact_web(self):
        # ic('contact_web')
        # company_id = self.env.user.company_id
        # company_ids = self.env.user.company_ids
        if self.env.is_admin():
            company_ids = self.env['res.company'].search([])
        else:
            # todo: error psycopg2.errors.UndefinedTable: relation "res_company_res_users_rel" does not exist
            # company_ids = self.env.user.sd_contacts_companies
            company_ids = self.env['res.company'].sudo().search([])
        show_projects = self.env['ir.config_parameter'].sudo().get_param('sd_contacts.show_projects')
        show_locations = self.env['ir.config_parameter'].sudo().get_param('sd_contacts.show_locations')
        show_job_title = self.env['ir.config_parameter'].sudo().get_param('sd_contacts.show_job_title')

        employee_list = self.sudo().search([('company_id', 'in', company_ids.ids), ('show_in_contact_list', '=', True)], order='sequence')
#         print(f'''
#
#                 {self.env.user.name}  is admin: {self.env.is_admin()}
#                 {company_ids}
#                 employee_list: {len(employee_list)}
#
# ''')
        contact_list = list([
            {
                'sequence' : rec.sequence,
                'id' : rec.id,
                'name' : rec.name,
                'work_phone' : rec.work_phone,
                'work_email' : rec.work_email,
                'work_location' : rec.work_location_id.name if show_locations else '',
                'hr_icon_display' : rec.hr_icon_display,
                'project' : rec.project_name.name if show_projects else '',
                'department' : rec.department_id.name,
                'parent_department_1' : rec.department_id.parent_id.name,
                'parent_department_2' : rec.department_id.parent_id.parent_id.name,
                'job_title' : rec.job_title if show_job_title else '',
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
        project_list = list({
                    rec.project_name.name for rec in employee_list if rec.project_name
                    })
        project_list.insert(0, _('All'))

        company_list = list([
            rec.name
            for rec in company_ids
        ])
        labels = {
            'title': _('Employees Contact Information'),
            'name': _('Name'),
            'depjob': f"{_('Job')} {_('Department')}",
            'location_project': f"{_('Location')} {_('Project')}",
            'phone': _('Phone'),
            'email': _('Email'),
            }
        # ic(contact_list, company_list, location_list, department_list)
        return json.dumps({'contact_list': contact_list,
                           'company_list': company_list,
                           'location_list': location_list,
                           'department_list': department_list,
                           'project_list': project_list,
                           'labels': labels,
                           'show': {'show_locations': show_locations,'show_projects': show_projects, }
                           })