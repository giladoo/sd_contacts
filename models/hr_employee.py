# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
import json
class HrEmployeeSdContacts(models.Model):
    _inherit = 'hr.employee'

    def contact_web(self):
        # company_id = self.env.user.company_id
        # company_ids = self.env.user.company_ids
        if self.env.is_admin():
            company_ids = self.env['res.company'].search([])
        else:
            company_ids = self.env.user.sd_contacts_companies
        employee_list =  self.sudo().search([('company_id', 'in', company_ids.ids)])
        print(f'''
                
                {self.env.user.name}  is admin: {self.env.is_admin()}
                {company_ids}
                employee_list: {len(employee_list)}

''')
        contact_list = list([
            {
                'id' : rec.id,
                'name' : rec.name,
                'work_phone' : rec.work_phone,
                'work_email' : rec.work_email,
                'department' : rec.department_id.name,
                'job_title' : rec.job_title,
                'company' : rec.company_id.name,
             }
            for rec in employee_list
        ])
        company_list = list([
            rec.name
            for rec in company_ids
        ])
        return json.dumps({'contact_list': contact_list, 'company_list': company_list})